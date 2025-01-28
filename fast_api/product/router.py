# Import necessary packages and modules
from fastapi import APIRouter, Depends
from fastapi_pagination import Page, paginate, add_pagination

# Import local dependencies and exceptions
from ..dependencies import (
    generate_qr_code,
    get_exception_responses,
    get_current_user,
    check_role_access,
    user_has_permission
)
from ..exceptions import (
    UnauthorizedException,
    PermissionException,
    DoesNotExist,
    InvalidIdException,
)
from ..responses import Success
from ..user.models import DBUser
from ..user.constants import Users, Roles
from ..company.constants import Locations
from ..company.models import Location
from ..report.service import create_report
from ..order.service import get_order_by_id
from .constants import Messages, Products
from . import service

# Create an API router for product-related endpoints
router = APIRouter(prefix="/products", tags=["products"])

# Endpoint to get product information by client email
@router.get("/{client_email}")
async def get_product_by_clientemail(client_email: str):
    client_data = {
        "client_email": client_email,
    }
    product_data = await service.find_products_by_client_email(client_data)
    return product_data

# Endpoint to generate QR codes
@router.get("/generate/qr", response_model=list)
async def generate(count: int):
    qr_codes = await generate_qr_code(count)
    return qr_codes

# Endpoint to get a paginated list of all products based on user role and permissions
@router.get(
    "/",
    response_model=Page[dict],
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def get_all_products(current_user: DBUser = Depends(get_current_user)):
    query = {Products.company: current_user.company}
    if current_user.role != Roles.admin:
        query[Products.warehouse] = current_user.warehouse
        if current_user.role != Roles.manager:
            query[Products.warehouse_team + "." + Users.id] = current_user.id
    products = await service.return_all_products(query)
    return paginate(products)

# Endpoint to get products for a specific order by order ID
@router.get(
    "/get_products_by/{order_id}",
)
async def get_products_by_orderID(
    order_id: str, current_user: DBUser = Depends(get_current_user)
):
    check_role_access(
        current_user.role,
        [
            Roles.admin,
            Roles.controller,
            Roles.warehouseman,
            Roles.manager,
            Roles.loader,
        ],
    )
    order_data = await get_order_by_id(order_id)
    query = {
        "order_id": order_id,
        "status": "product_arrived",
        "warehouse": current_user.warehouse,
    }
    return_message = ""
    products = await service.return_all_products(query)
    quantity_of_missing_product = len(order_data["products"]) - len(products)
    if quantity_of_missing_product > 0:
        return_message = f"missing in the order of {quantity_of_missing_product} goods"
    else:
        return_message = "in this order all goods are"
    # report_data={
    #     "order_id":order_id,
    #     "description":return_message
    # }
    # await create_report(report_data)
    result = {
        "message": return_message,
        "products_in_order": order_data["products"],
        "products_arrived_in_warehouse": products,
    }
    return result

# Endpoint to get product information by product ID
@router.get(
    "/{product_id}",
    response_model=dict,
    responses=get_exception_responses(DoesNotExist),
)
async def get_product(
    product_id: str, current_user: DBUser = Depends(get_current_user)
):
    # Verify the information of the product by scanning its QR code
    if current_user.role != Roles.admin and current_user.role != Roles.manager:
        await service.check_access_product_by_worker_id(product_id, current_user.id)
    product = await service.get_product_by_id_(product_id)
    return product

# Endpoint to relocate a product to a new location
@router.put(
    "/{product_id}/relocate",
    response_model=Success,
    responses=get_exception_responses(
        UnauthorizedException, PermissionException, DoesNotExist, InvalidIdException
    ),
)
async def relocate_product(
    product_id, location: Location, current_user: DBUser = Depends(get_current_user)
):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"relocate_product")
    # check_role_access(current_user.role, [Roles.warehouseman, Roles.loader])
    await service.check_access_product_by_worker_id(product_id, current_user.id)
    locations_dict = location.dict()
    new_location = {
        Users.user_id: current_user.id,
        Locations.warehouse_row: locations_dict["warehouse_row"],
        Locations.shelf_num: locations_dict["shelf_num"],
        Locations.floor_level: locations_dict["floor_level"],
    }
    await service.update_product(product_id, new_location)
    return {Messages.message: Messages.pr_reloc_scs}

# Endpoint to get the total quantity of a product by its name
@router.get("/product_by/{product_name}", response_model=dict)
async def get_product_by_product_name(
    product_name: str, current_user: DBUser = Depends(get_current_user)
):
    query = {
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_product_by_name")
    # check_role_access(current_user.role, [
    #     Roles.admin, Roles.manager,
    #     Roles.controller, Roles.employee,
    #     Roles.loader, Roles.warehouseman
    # ])
    result = await service.get_total_quantity_product_by_name(product_name)
    return result

# Add pagination to the router
add_pagination(router)
