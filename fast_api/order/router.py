# Installed packages
from fastapi import APIRouter, Query, File, Depends, UploadFile
from fastapi.params import Path
from typing import Union, Optional,List
from fastapi_pagination import Page, paginate, add_pagination
from bson import ObjectId
from datetime import datetime,timedelta
import json

# Local packages
# from ..websocket.manager import ConnectionManager
from ..warehouse.service import get_product_warehouse_category
from ..redis import redis_set, redis_verify, delete
from ..dependencies import (
    get_exception_responses,
    get_current_user,
    check_role_access,
    check_admin_n_manager_access_without_exc,
    generate_unique_url,
    check_order_creation_token,
    upload_files,
    generate_random_password,
    generate_random_code,
    user_has_permission
)
from ..exceptions import (
    UnauthorizedException,
    PermissionException,
    DoesNotExist,
    TokenInvalidException,
    DuplicateKeyException,
    AlreadyExistsException,
    NotFoundException,
    ConflictException,
    EmptyFileUploadException,
    RequestEntityTooLargeException,
    UnsupportedMediaTypeException,
    AlreadyAssignedException,
    BaseAPIException,
    LogicBrokenException,
)
# from ..service import check_company_warehouse
from ..user.utils import hash_password
from ..responses import Success
from ..user.models import DBUser
from ..product.models import ManagerSideProduct
from ..company.service import (
    check_order_company_and_or_warehouse,
    get_company
)
from ..company.constants import Company, Warehouses
from ..websocket.router import manager
from . import service
from .email_sender import send_email_to_client
from .constants import Orders, Messages
from .models import Order, SalesmanSideOrder, OrderWithId
from ..config import URL_PARTS, DOCUMENTS_DIRECTORY, MAX_DOCUMENT_UPLOAD_SIZE
from urllib.parse import quote, unquote
from ..user.service import (
    add_order_to_users,
    add_order_to_salesman,
    check_employee_schedule,
    users_by_order_id,
    start_user_work,
    register_user_
)
from ..user.constants import Users, Roles
# Define a FastAPI router for order-related endpoints.
router = APIRouter(prefix="/orders", tags=["orders"])
# conn_manager = ConnectionManager()
# Initialize the connection manager if used for WebSocket communication.

# Define various endpoint handlers for order management.

# Handler to retrieve a list of users in an order team.
@router.get("/{order_id}/team", response_model=list[Order])
async def order_id_in_users(
    order_id: str, current_user: DBUser = Depends(get_current_user)
):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    # Check user's role for access control.
    await user_has_permission(query=query,required_permission="view_order_team")
    check_role_access(current_user.role, [Roles.director, Roles.manager])
    res = await users_by_order_id(order_id)
    return res

# Handler to initiate work on an order.
@router.get("/{order_id}/start")
async def start_work(order_id: str, current_user: DBUser = Depends(get_current_user)):
    # Start work on the specified order.
    await start_user_work(order_id, current_user.id, datetime.now())
    # Send a WebSocket message to inform the user.
    await manager.send_message(
        current_user.id,
        json.dumps(
            {Users.role: current_user.role, Orders.status: Messages.status_started}
        ),
    )
    return {"success": "started working"}

# Handler to retrieve a paginated list of all orders.
@router.get(
    "/",
    response_model=Page[dict],
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def get_all_orders(current_user: DBUser = Depends(get_current_user)):
    # Retrieve orders based on user's role and access.
    await user_has_permission({"role_name":current_user.role,"company_name":current_user.company},
                              required_permission="view_all_orders")
    orders = await service.return_all_orders(
        current_user.id, current_user.role, current_user.company, current_user.warehouse
    )
    # return orders
    return paginate(orders)

# Handler to retrieve detailed information about a specific order.
@router.get(
    "/{order_id}/info",
    response_model=dict,
    responses=get_exception_responses(
        UnauthorizedException, PermissionException, DoesNotExist
    ),
)
async def get_order(order_id: str, current_user: DBUser = Depends(get_current_user)):
    query = {Orders.id: ObjectId(order_id)}
    if check_admin_n_manager_access_without_exc(current_user.role):
        if current_user.role == Roles.salesman:
            query[Orders.salesman_id] = current_user.id
        else:
            query[Orders.warehouse_team + "." + Users.id] = current_user.id
        await service.check_access_order_by_employee_id(query)
    order = await service.get_order_by_id(order_id)
    return order

# Handler to retrieve non-checked products in an order.
@router.get(
    "/{order_id}/unchecked_products",
    response_model=list,
    responses=get_exception_responses(
        UnauthorizedException, PermissionException, DoesNotExist
    ),
)
async def non_checked_order_products(
    order_id: str, current_user: DBUser = Depends(get_current_user)
):
    # Check user's role for access control.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="view_unchecked_products")
    query =None
    # check_role_access(current_user.role, [Roles.controller])
    # Define a query to check access to the order.
    query = {
        Orders.id: ObjectId(order_id),
        Orders.warehouse_team + "." + Users.id: current_user.id,
    }
    # Check access to the order by employee ID.
    await service.check_access_order_by_employee_id(query)
    # Retrieve non-checked products in the order.
    non_checked_products = await service.get_order_products_filtered_by_status(order_id)
    return non_checked_products

# Handler to create a new order.
@router.post(
    "/",
    response_model=Success,
    responses=get_exception_responses(
        TokenInvalidException, DuplicateKeyException, DoesNotExist
    ),
)
async def create_order(
    order: Order,
    company: Union[str, None] = Query(default=None, max_length=100),
    token: Union[str, None] = Query(default=None, max_length=100),
):
    # Convert the order input to a dictionary.
    order = order.dict()
    
    # Validate the order creation token.
    await check_order_creation_token(token)
    token = unquote(token)
    company = unquote(company)
    
    # Retrieve company data based on the provided company name.
    company_data = await get_company(company)
    
    # Generate a random password for the client user.
    password = await generate_random_password()
    hashed_password = hash_password(password=password)
    verification_code = await generate_random_code()
    # Create a user object for the client.
    user ={
        "firstname": order["first_name"],
        "lastname": order["second_name"],
        "role": Roles.client,
        "email": order["e_mail"],
        "verification_code":verification_code,
        "company": company,
        "hashed_password": hashed_password,
        "telephone": order["telephone"],
        "user_address": order["user_address"],
        "is_confirmed":False,
    }
    # salesman_id = await redis_verify(token)
    # print("*****",salesman_id)
    salesman_id = await service.validate_token_and_get_salesman_id(token)
    order[Orders.recipient] = company
    order[Orders.salesman_id] = salesman_id
    order[Orders.status] = Messages.st_or_added
    
    # Register the client user.
    await register_user_(user=user)
    for product in order["products"]:
        product["volume"]=product["length"]*product["width"]*product["height"]
    # Register the order and associate it with the salesman.
    order_id = await service.register_order(order)
    await add_order_to_salesman(salesman_id, order_id)
    
    # Prepare an email description for the client.
    description = f"""
        <html>
        <head>
            <style>
                /* Добавьте стили CSS по вашему усмотрению */
            </style>
        </head>
        <body>
            <p>Dear Valued Client,</p>
            <p>Thank you for your order. We have received and saved it with the following details:</p>
            <ul>
                <li>Order ID: {order_id}</li>
                <li>Your login credentials for the warehouse management system are:</li>
                <ul>
                    <li>Email: {user['email']}</li>
                    <li>Password: {password}</li>
                    <li>Verification code: {verification_code}</li>
                </ul>
                <li>Website: <a href="https://warehouse-main.vercel.app/auth/verification">Use this link</a></li>
            </ul>
            <p>Please login using these credentials to view the status of your order, track shipments, and manage any additional orders.</p>
            <p>If you have any other questions, please contact us at <a href="mailto:noreply@prometeochain.io">noreply@prometeochain.io</a>. We're here to help!</p>
            <p>Thank you for choosing us. Have a great day!</p>
        </body>
        </html>
        """
    
    # Prepare email data and send an order confirmation email to the client.
    email_data ={
        "office_email":company_data["office_email"],
        # "office_password":company_data["office_password"],
        "order_id":order_id,
        "recipient_email":order["e_mail"],
        "description" : description,
        "subject":"Order Confirmation",
    }
    await send_email_to_client(email_data=email_data)
    # await delete(token)
    await service.delete_token(token)

    return {Messages.message: Messages.or_reg_scs}

# Handler to update an existing order.
@router.put(
    "/{order_id}",
    response_model=dict,
    responses=get_exception_responses(
        TokenInvalidException, DuplicateKeyException, DoesNotExist
    ),
)
async def update_order(
    updated_fields: Order,
    order_id: str,
    token: Union[str, None] = Query(default=None, max_length=100),
):
    # Check and validate the order creation token.
    await check_order_creation_token(token)
    token = unquote(token)
    order_id = unquote(order_id)
    # Retrieve the existing order.
    order = await service.get_order_by_id(order_id)
    # Update the order fields with the provided values.
    for field, value in updated_fields.model_dump().items():
        order[field] = value
    # Update the order in the database.
    await service.update_order(order_id, order)
    # Delete the used token.
    await service.delete_token(token)
    return {Messages.message: Messages.or_up_scs}

@router.delete("/{order_id}",response_model=dict)
async def delete_order_by_id(order_id:str,
                             current_user:DBUser=Depends(get_current_user)):
    # Check user's role for access control.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="delete_main_order")
    query =None
    order_data = await service.get_order_by_id(order_id=order_id)
    if order_data["status"]=="divided_order":
        for order in order_data["sub_orders"]:
            await service.delete_order_by_order_id({"_id":ObjectId(order["id"])})
    await service.delete_order_by_order_id(query={"_id":ObjectId(order_id)})
    return {"success":f"successfully deleted order by id {order_id}"}

# Handler to create an invoice for an order.
@router.put(
    "/{order_id}/invoice",
    response_model=Success,
    responses=get_exception_responses(
        UnauthorizedException,
        PermissionException,
        DoesNotExist,
        AlreadyExistsException,
        AlreadyAssignedException,
        LogicBrokenException,
    ),
)
async def manager_register(
    # webscoket:WebSocket,
    order_id:str,
    workers: ManagerSideProduct,
    current_user: DBUser = Depends(get_current_user),
):
    try:
        # Check if the current user has the required role for access.
        query ={
            "role_name":current_user.role,
            "company_name":current_user.company
        }
        await user_has_permission(query=query,
                                  required_permission="create_invoice")
        query=None
        # check_role_access(
        #     current_user.role, [Roles.director, Roles.admin, Roles.manager]
        # )
        # Convert the ManagerSideProduct input to a dictionary.
        data = workers.dict() 
        # Check the coherence and status of the order.
        await service.check_coherence(
            {Orders.id: order_id, Orders.status: Messages.status_invoiced}
        )
        
        # Extract relevant data from the input.
        extracted_data = {
            Orders.initial_schedule: data[Orders.initial_schedule],
            Orders.initial_time: data[Orders.initial_schedule],
            Orders.end_schedule: data[Orders.end_schedule],
            Orders.end_time: data[Orders.end_time],
            Orders.warehouse_team: [
                ObjectId(obj[Users.id]) for obj in data[Orders.warehouse_team]
            ],
        }
        # Prepare data for the user order.
        user_order = {"order_id": order_id}
        user_order.update(data)
        user_order.pop("warehouse_team")
        user_order.pop("place")
        user_order.update({"status": "not started"})
        # Update the order with the invoice data.
        data[Users.manager_id] = current_user.id
        data[Orders.status] = Messages.status_invoiced
        await service.update_order_invoice(order_id, data)
        # Get the list of users associated with the order.
        users = data[Orders.warehouse_team]
        # Add the order to the users.
        await add_order_to_users(user_order, users) 
        # Notify users about being added to the order.
        message = f"You have been added to order {order_id}"
        for user in users:
            # Send a notification message to each user.
            await manager.send_message(user["id"], message=message)
    except BaseAPIException as e:
        raise e
    
    return {Messages.message: Messages.or_inv_reg_scs}

# Handler to approve or reject order products.
@router.put(
    "/{order_id}/approve",
    response_model=Success,
    responses=get_exception_responses(
        UnauthorizedException, PermissionException, DoesNotExist
    ),
)
async def approve_order_products(
    order_id: str, approve: bool, current_user: DBUser = Depends(get_current_user)
):
    # Check if the current user has the required role for access.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"approve_order_products")
    # check_role_access(current_user.role, [Roles.manager])
    # Determine the order status based on the approval decision.
    if approve:
        status = Messages.status_approve
    else:
        status = Messages.status_failed
    # Update the order status.
    await service.update_order_status(order_id, status)
    return {Messages.message: Messages.or_approv_scs}

# Handler to update the status of an order for loaders.
@router.put("/{order_id}/loader", response_model=Success)
async def update_status(
    order_id: str, current_user: DBUser = Depends(get_current_user)
):
    # Check if the current user has the required role for access.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"update_order_status")
    # check_role_access(current_user.role, [Roles.loader])
    # Update the order status to indicate completion.
    order_data = await service.update_order_status(order_id, Messages.or_compl_scs)
    return order_data
# Add pagination support to the router.

add_pagination(router)
