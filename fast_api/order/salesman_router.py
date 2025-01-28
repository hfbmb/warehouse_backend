# Import FastAPI dependencies
from fastapi import APIRouter, File, Depends, UploadFile, Path
from fastapi_pagination import Page, paginate, add_pagination
from bson.objectid import ObjectId
from datetime import datetime

# Import local packages and services
from ..warehouse.service import get_product_warehouse_category, boxes_with_product
from ..dependencies import (
    get_exception_responses,
    get_current_user,
    generate_unique_url,
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
from ..user.models import DBUser
from ..company.service import check_order_company_and_or_warehouse
from ..company.constants import Company
from . import service
from .constants import Orders, Messages
from .models import SalesmanSideOrder, SalesmanProductTobox, SubOrders
from ..config import URL_PARTS, DOCUMENTS_DIRECTORY, MAX_DOCUMENT_UPLOAD_SIZE
from urllib.parse import quote

# Initialize API router with prefix and tags
salesman_router = APIRouter(prefix="/salesman", tags=["salesman"])

# Endpoint to generate a unique URL for a salesperson
@salesman_router.get(
    "/generate_url/",
    response_model=dict,
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def generate_url(current_user: DBUser = Depends(get_current_user)):
    # Check for user permissions
    query = {
        "role_name": current_user.role,
        "company_name": current_user.company
    }
    await user_has_permission(query=query, required_permission="generate_sales_url")
    # Generate a unique URL token
    token = await generate_unique_url()
    encoded_token = quote(token)
    encoded_company = quote(current_user.company)
    # Construct the URL
    url = (
        f"{URL_PARTS['HTTP']}://{URL_PARTS['DOMAIN_NAME']}/{URL_PARTS['ENDPOINT']}?"
        f"{URL_PARTS['COMPANY']}={encoded_company}&{URL_PARTS['TOKEN']}={encoded_token}"
    )
    created_at = datetime.now()
    # Store the token
    await service.create_token(token, current_user.id, created_at)
    return {"url_link": url, "createdAt": created_at}

# ... (other endpoints with comments)

# Endpoint to generate a URL for updating an existing order
@salesman_router.get(
    "/{order_id}/generate_url_update",
    response_model=dict,
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def generate_url_update(
    order_id: str, current_user: DBUser = Depends(get_current_user)
):
    # Check for user permissions
    query = {
        "role_name": current_user.role,
        "company_name": current_user.company
    }
    await user_has_permission(query=query, required_permission="generate_order_update_url")
    # Retrieve the existing order by its ID
    order = await service.get_order_by_id(order_id)
    # Generate a unique URL token
    token = await generate_unique_url()
    encoded_token = quote(token)
    encoded_id = quote(order_id)
    # Construct the URL for updating the order
    url = (
        f"{URL_PARTS['HTTP']}://{URL_PARTS['DOMAIN_NAME']}/{URL_PARTS['ENDPOINT']}?"
        f"{URL_PARTS['ORDER_ID']}={encoded_id}&{URL_PARTS['TOKEN']}={encoded_token}"
    )
    created_at = datetime.now()
    # Store the token
    await service.create_token(token, current_user.id, created_at)
    return {"url_link": url, "createdAt": created_at}

# Endpoint to get all sub-orders by a main order ID
@salesman_router.get("/{order_id}", response_model=Page[dict])
async def get_all_sub_order_by_order_id(
    order_id: str, current_user: DBUser = Depends(get_current_user)
):
    # Check for user permissions
    query = {
        "role_name": current_user.role,
        "company_name": current_user.company
    }
    await user_has_permission(query=query, required_permission="view_all_orders")
    query=None
    # Query to find sub-orders related to the main order
    query = {
        "main_order_id": order_id
    }
    sub_orders = await service.get_all_sub_orders(query=query)
    return sub_orders

# ... (other endpoints with comments)
# Endpoint to create a sub-order
@salesman_router.post("/", response_model=dict)
async def create_sub_order(orders: SubOrders, current_user: DBUser = Depends(get_current_user)):
    # Check for user permissions
    query = {
        "role_name": current_user.role,
        "company_name": current_user.company
    }
    await user_has_permission(query=query, required_permission="create_sub_order")
    # Retrieve the main order by its ID
    _ = await service.get_order_by_id(order_id=orders.order_id)
    # Initialize an empty list to store sub-order IDs
    orders_id = []
    # Loop through the sub-orders and create them
    for order in orders.sub_orders:
        order["main_order_id"] = orders.order_id
        order_id = await service.register_order(order=order)
        orders_id.append(order_id)
    # Update the main order to include the sub-order IDs
    await service.update_order(order_id=orders.order_id, data={"sub_orders": orders_id, "status": "divided_order"})
    return {"success": f"Successfully divided main order by {orders['order_id']}"}

# Endpoint to record sales-related information for an order
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
    salesman_order: SalesmanSideOrder = Depends(SalesmanSideOrder),
    current_user: DBUser = Depends(get_current_user),
    order_id: str = Path(...),
    file: UploadFile = File(None),
):
    # Check for user permissions
    query = {
        "role_name": current_user.role,
        "company_name": current_user.company
    }
    await user_has_permission(query=query, required_permission="record_sales_info")
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


# # Endpoint to allocate products to boxes
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
    # Initialize an empty list to store boxes
    order_data["boxes"] = []
    # Allocate products to boxes
    data = data.dict()
    await boxes_with_product(data=data)
    order_data["boxes"].append(data)
    # Remove unnecessary keys from the order data
    order_data.pop("products")
    order_data.pop("id")
    # Update the order with the new box allocation
    await service.update_order_invoice(order_id=order_id, data=order_data)
    return {"success": "Successfully allocated product in box"}

