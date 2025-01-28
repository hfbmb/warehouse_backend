from fastapi import APIRouter,Depends
from fastapi_pagination import Page, paginate, add_pagination
from ..exceptions import (
    UnauthorizedException,
    PermissionException,
)
#local imports
from ..company import constants
from ..company.service import check_order_company_and_or_warehouse,get_company
from .models import Warehouse,UpdateWarehouse
from ..user.models import DBUser, UserWithID
from ..user.constants import Roles
from ..user.service import (
    remove_all_users_in_warehouse,
    get_all_users_by_warehouse,
    # remove_user
)
from ..dependencies import (
    check_role_access,
    get_exception_responses,
    get_current_user,
    user_has_permission
)
from . import service

# Create an APIRouter instance for warehouse-related operations.
warehouse_router = APIRouter(
    prefix=constants.Warehouses.prefix, tags=[constants.Warehouses.warehouse]
)
# Define a GET endpoint to retrieve the current user's warehouse by warehouse_name.
@warehouse_router.get("/{warehouse_name}", response_model=dict)
async def get_current_user_warehouse(
    warehouse_name: str, current_user: DBUser = Depends(get_current_user)
):
    # Construct a query to fetch the warehouse associated with the current user's company and the specified name.
    query = {
        constants.Company.company_name: current_user.company,
        constants.Warehouses.warehouse_name: warehouse_name,
    }
    # Call the service function to retrieve the warehouse information.
    warehouse = await service.current_user_warehouse(query)
    # Return the retrieved warehouse information.
    return warehouse

@warehouse_router.get("/",response_model=Page[dict])
async def get_all_warehouses_by_company_name(current_user:DBUser=Depends(get_current_user)):
    # check_role_access(current_user.role,[Roles.director,Roles.admin])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"view_all_warehouses")
    query ={}
    if current_user.role ==Roles.admin:
        query ={}
    elif current_user.role ==Roles.director or current_user.role ==Roles.salesman:
        query ={"company_name":current_user.company}
    warehouses = await service.get_all_warehouses(query=query)
    return paginate(warehouses)

@warehouse_router.get("/{warehouse_id}",response_model=dict)
async def get_warehouse_by_id(warehouse_id:str,current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"view_warehouse_by_id")
    # check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.director])
    warehouse = await service.get_warehouse_by_id(id=warehouse_id)
    return warehouse

# Define a GET endpoint to retrieve users associated with a warehouse.
@warehouse_router.get(
    "/users/",
    response_model=Page[UserWithID],
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def get_warehouse_users(user: DBUser = Depends(get_current_user)):
    # Check if the current user has the necessary role to access warehouse users.
    query ={
        "role_name":user.role,
        "company_name":user.company
    }
    await user_has_permission(query,"view_warehouse_users")
    # check_role_access(user.role, [Roles.director, Roles.admin, Roles.manager])
    # Retrieve and paginate the list of users associated with the current user's company and warehouse.
    users = await get_all_users_by_warehouse(user.company, user.warehouse)
    # Return the paginated list of warehouse users.
    return paginate(users)

# Define a POST endpoint to add a new warehouse to the company.
@warehouse_router.post("/")
async def add_warehouse_company(
    warehouse_data: Warehouse,
    current_user: DBUser = Depends(get_current_user),
):
    # Check if the current user has the necessary role to add a warehouse.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"add_warehouse")
    query =None
    # check_role_access(current_user.role, [Roles.director, Roles.admin,Roles.manager])
    query ={
        "company_name":current_user.company,
    }
    await check_order_company_and_or_warehouse(query=query)
    # Add the new warehouse to the company using the provided data.
    await service.create_warehouse(current_user.company, warehouse_data.dict())
    # Return a success message after successfully adding the warehouse.
    return {"success": "added warehouse"}

# Define a PUT endpoint to update warehouse data by name.
@warehouse_router.put("/{warehouse_name}")
async def update_warehouse_data(
    warehouse_name: str,
    warehouse_data: UpdateWarehouse,
    current_user: DBUser = Depends(get_current_user),
):
    # Check if the current user has the necessary role to update warehouse data.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"update_warehouse")
    query=None
    # check_role_access(current_user.role, [Roles.manager, Roles.director, Roles.admin])
    # Create a dictionary to store updated warehouse data.
    warehouse_dict = warehouse_data.dict()
    # Determine the target warehouse name for the update.
    if warehouse_name:
        warehouse_dict[constants.Warehouses.warehouse_name] = warehouse_name
    else:
        warehouse_dict[constants.Warehouses.warehouse_name] = current_user.warehouse
    # Create a filtered data dictionary to exclude empty or null values.
    query ={"company_name":current_user.company,"warehouse_name":warehouse_dict[constants.Warehouses.warehouse_name]}
    data = {}
    for key, value in warehouse_dict.items():
        if value is not None and value != "" and value != "string" and value != 0:
            data[key] = value
    # Call the service function to update warehouse data.
    await service.update_warehouse_data(query=query,warehouse_data= data)
    # Return a success message after successfully updating warehouse data.
    return {"success": "updated data"}

# Define a DELETE endpoint to delete a warehouse by name.
@warehouse_router.delete("/{warehouse_name}")
async def delete_warehouse(
    warehouse_name: str, current_user: DBUser = Depends(get_current_user)
):
    # Check if the current user has the necessary role to delete a warehouse.
    # check_role_access(current_user.role, [Roles.director, Roles.admin])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"delete_warehouse")
    # Construct a query to delete the specified warehouse or the current user's warehouse.
    warehouse_query = {
        constants.Company.company_name: current_user.company,
        constants.Warehouses.warehouse_name: (
            warehouse_name if warehouse_name else current_user.warehouse
        ),
    }
    # Call service functions to delete the warehouse and associated users.
    await service.warehouse_delete(warehouse_query)
    await remove_all_users_in_warehouse(warehouse_query)
    # Return a success message after successfully deleting the warehouse.
    return {"message": "successfully deleted"}

# Define a DELETE endpoint to delete a gate by gate name.
@warehouse_router.delete("/gates/{gate_name}")
async def delete_gate_by_gatename(gate_name: str, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the necessary role to delete a gate.
    # check_role_access(current_user.role, [Roles.director, "manager", Roles.admin])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"delete_gate")
    # Prepare the data dictionary for deleting the gate by gate name.
    data = {
        "company_name": current_user.company,
        "warehouse_name": current_user.warehouse,
        "gate_name": gate_name
    }
    # Call the service function to delete the gate by gate name.
    result = await service.delete_gate_by_gate_name(data)
    if result:
        return result
    else:
        # Handle the case where the result is empty (possibly an error).
        # You may want to log or handle this case accordingly.
        pass
# Add pagination support to the warehouse_router.
add_pagination(warehouse_router)