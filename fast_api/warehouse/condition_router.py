from fastapi import APIRouter, Depends
from bson.objectid import ObjectId
from fastapi_pagination import Page, paginate, add_pagination
from ..dependencies import (
    check_role_access,
    get_exception_responses,
    get_current_user,
)
from ..user.models import DBUser
from ..user.constants import Roles
from .models import Condition, ConditionUpdate
from .service import (create_condition, get_condition_by_id, 
                      update_conditions, get_all_conditions, 
                      check_zone_by_id,delete_condition_by_qurey)

# Create an APIRouter instance for warehouse-related operations.
condition_router = APIRouter(
    prefix="/condition", tags=["condition"]
)

# Endpoint to create a new condition.
@condition_router.post("/", response_model=dict)
async def create_condition_data(data: Condition, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    check_role_access(current_user.role, [Roles.manager, Roles.admin, Roles.director])
    # Check if the specified zone (by ID) exists.
    await check_zone_by_id(data.zone_id)
    # Create a new condition based on the provided data.
    await create_condition(data=data.dict())
    # Return a success message.
    return {"success": "Successfully created condition"}

# Endpoint to get condition data by its ID.
@condition_router.get("/{condition_id}", response_model=dict)
async def get_condition_data_by_id(condition_id: str, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    check_role_access(current_user.role, [Roles.manager, Roles.admin, Roles.director])
    # Get condition data by its ID.
    res = await get_condition_by_id(id=condition_id)
    # Return the retrieved condition data.
    return res

# Endpoint to get all condition data.
@condition_router.get("/", response_model=Page[dict])
async def get_all_order_data(current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    check_role_access(current_user.role, [Roles.admin, Roles.manager, Roles.director])
    # Retrieve all condition data.
    results = await get_all_conditions({})
    # Return a list of all condition data.
    return paginate(results)

# Endpoint to update condition data by ID.
@condition_router.put("/{condition_id}", response_model=dict)
async def update_condition_data_by_id(condition_id: str, data: ConditionUpdate, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    check_role_access(current_user.role, [Roles.admin, Roles.manager, Roles.director])
    # Define the query to identify the condition by its ID.
    query = {"_id": ObjectId(condition_id)}
    data = data.dict()
    condition_d ={}
    for key,val in data.items():
        if val !=None and val !="string" and val !=0:
            condition_d[key]=val
    # Update the condition data with the provided values from ConditionUpdate.
    await update_conditions(query=query, data=condition_d)
    # Return a success message.
    return {"success": "Successfully updated condition data"}


##Endpoint to delete condition by Id
@condition_router.delete("/{condition_id}",response_model=dict)
async def delete_condition(condition_id:str,current_user:DBUser=Depends(get_current_user)):
    check_role_access(current_user.role, [Roles.admin, Roles.manager, Roles.director])
    query = {"_id": ObjectId(condition_id)}
    await delete_condition_by_qurey(query=query)
    return {"success":f"successfully deleted condition by {condition_id}"}

@condition_router.get("/zone/{zone_id}",response_model=Page[dict])
async def get_conditions_by_zoneid(zone_id:str,current_user:DBUser=Depends(get_current_user)):
    check_role_access(current_user.role, [Roles.admin, Roles.manager, Roles.director])
    query ={
        "zone_id":zone_id
    }
    conditions = await get_all_conditions(query=query)
    return paginate(conditions)


add_pagination(condition_router)
