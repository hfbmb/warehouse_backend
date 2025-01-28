# Installed packages
from fastapi import APIRouter, File, Depends, UploadFile
from fastapi.params import Path
# from typing import Union, Optional,List
from fastapi_pagination import Page, paginate, add_pagination
from bson import ObjectId
from datetime import datetime
# import json

# Local packages
# from ..websocket.manager import ConnectionManager
from ..warehouse.service import get_product_warehouse_category,boxes_with_product
# from ..redis import redis_set, redis_verify, delete
from ..dependencies import (
    get_exception_responses,
    get_current_user,
    # check_role_access,
    # check_admin_n_manager_access_without_exc,
    generate_unique_url,
    # check_order_creation_token,
    upload_files,
    user_has_permission
)
from ..exceptions import (
    UnauthorizedException,
    PermissionException,
    DoesNotExist,
    AlreadyExistsException,
    NotFoundException,
    ConflictException,
    EmptyFileUploadException,
    RequestEntityTooLargeException,
    UnsupportedMediaTypeException,
)
# from ..service import check_company_warehouse
from ..user.utils import hash_password
# from ..responses import Success
from ..user.models import DBUser
# from ..product.models import ManagerSideProduct
from ..company.service import (
    check_order_company_and_or_warehouse,
    # get_company
)
from ..company.constants import Company
from ..websocket.router import manager
from . import service
# from .email_sender import send_email_to_client
from .constants import Orders, Messages
from .models import SalesmanSideOrder,SalesmanProductTobox
from ..config import URL_PARTS, DOCUMENTS_DIRECTORY, MAX_DOCUMENT_UPLOAD_SIZE
from urllib.parse import quote

salesman_router = APIRouter(prefix="/salesman",tags=["salesman"])

# Handler to generate a URL for a salesperson.
@salesman_router.get(
    "/generate_url/",
    response_model=dict,
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def generate_url(current_user: DBUser = Depends(get_current_user)):
    # Check user's role for access control.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="generate_sales_url")
    # check_role_access(current_user.role, [Roles.salesman])
    # Generate a unique token for the URL.
    token = await generate_unique_url()
    encoded_token = quote(token)
    encoded_company = quote(current_user.company)
    # Construct the URL with the token and company information.
    url = (
        f"{URL_PARTS['HTTP']}://{URL_PARTS['DOMAIN_NAME']}/{URL_PARTS['ENDPOINT']}?"
        f"{URL_PARTS['COMPANY']}={encoded_company}&{URL_PARTS['TOKEN']}={encoded_token}"
    )
    created_at = datetime.now()
    # redis_data = {"token_data": token, "salesman_id": current_user.id}
    # set_data = "token"
    # await redis_set(set_data, redis_data)
    await service.create_token(token, current_user.id, created_at)
    return {"url_link": url, "createdAt": created_at}

# Handler to generate a URL for updating an existing order.
@salesman_router.get(
    "/{order_id}/generate_url_update",
    response_model=dict,
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def generate_url_update(
    order_id: str, current_user: DBUser = Depends(get_current_user)
):
    # Check user's role for access control.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="generate_order_update_url")
    # check_role_access(current_user.role, [Roles.salesman])
    # Retrieve the order.
    order = await service.get_order_by_id(order_id)
    # Validate that the salesman has permission for the order.
    await service.validate_salesman(order[Orders.salesman_id], current_user.id)
    # Generate a unique token for the URL.
    token = await generate_unique_url()
    encoded_token = quote(token)
    encoded_id = quote(order_id)
    # Construct the URL with the token and order ID.
    url = (
        f"{URL_PARTS['HTTP']}://{URL_PARTS['DOMAIN_NAME']}/{URL_PARTS['ENDPOINT']}?"
        f"{URL_PARTS['ORDER_ID']}={encoded_id}&{URL_PARTS['TOKEN']}={encoded_token}"
    )
    created_at = datetime.now()
    redis_data = {"token_data": token, "salesman_id": current_user.id}
    # await redis_set(encoded_token, redis_data)
    await service.create_token(token, current_user.id, created_at)

    return {"url_link": url, "createdAt": created_at}



# Handler to record sales-related information for an order.
@salesman_router.put(
    "/{order_id}/record",
    response_model=dict,
    responses=get_exception_responses(
        UnauthorizedException,
        PermissionException,
        DoesNotExist,
        AlreadyExistsException,
        NotFoundException,
        ConflictException,
        EmptyFileUploadException,
        RequestEntityTooLargeException,
        UnsupportedMediaTypeException,
    ),
)
async def salesman_register(
    # document_pdf: Optional[List[UploadFile]]=File(None),
    salesman_order: SalesmanSideOrder = Depends(SalesmanSideOrder),
    current_user: DBUser = Depends(get_current_user),
    order_id: str = Path(...),
    file: UploadFile = File(None),
):  
    # Check user's role for access control.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="record_sales_info")
    query=None
    # check_role_access(current_user.role, [Roles.salesman])
    # Check coherence and status of the order.
    await service.check_coherence(
        {Orders.id: order_id, Orders.status: Messages.status_salesman_recorded}
    )
    # Convert the salesman_order input to a dictionary.
    salesman_order = salesman_order.dict()
    salesman_order["salesman_id"]=current_user.id
    # Check if the provided company and warehouse are valid.
    await check_order_company_and_or_warehouse(
        {
            Company.company_name: current_user.company,
        }
    )
    # Upload and store a document file if provided.
    if file:
        document_pdf = []
        document_pdf.append(file)
        file_paths = upload_files(
            document_pdf, order_id, MAX_DOCUMENT_UPLOAD_SIZE, DOCUMENTS_DIRECTORY
        )
        salesman_order[Orders.document_pdf] = file_paths
    order_data = await service.get_order_by_id(order_id = order_id)
    salesman_order["products"]=[]
    query ={"company_name":current_user.company,
            "warehouse_name":salesman_order["warehouse_name"]}
    for product in order_data["products"]:
        product_data = await get_product_warehouse_category(query=query,product_data=product)
        salesman_order["products"].append(product_data)
    # Update the order status to "Salesman Recorded."
    salesman_order[Orders.status] = Messages.status_salesman_recorded
    # Update the order invoice in the database.
    await service.update_order_invoice(order_id, salesman_order)
    return {Messages.message: Messages.or_rrd_scs}

@salesman_router.put("/{order_id}/product/allocation",response_model=dict)
async def product_allocate(order_id:str,
                           data:SalesmanProductTobox,
                           current_user:DBUser=Depends(get_current_user)):
    # Check user's role for access control.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="record_sales_info")
    query=None
    order_data = await service.get_order_by_id(order_id=order_id)
    order_data["boxes"]=[]
    data=data.dict()
    await boxes_with_product(data=data)
    order_data["boxes"].append(data)
    order_data.pop("products")
    order_data.pop("id")
    await service.update_order_invoice(order_id=order_id,data=order_data)

    return {"success":"successfully allocate product in box"}
