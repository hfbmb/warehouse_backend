from fastapi import APIRouter, Depends
from bson.objectid import ObjectId
from fastapi_pagination import Page, paginate, add_pagination
from ..dependencies import (
    check_role_access,
    # get_exception_responses,
    get_current_user,
    user_has_permission
)
from ..user.models import DBUser
from ..user.constants import Roles
from .models import Racks, RackUpdate
from .service import (create_rack, get_rack_by_id, 
                      update_racks, get_all_racks,get_zone_by_id,
                      delete_rack_by_id
                      )

# Create an APIRouter for the /rack endpoint with associated tags.
rack_router = APIRouter(prefix="/rack", tags=["rack"])

# Endpoint to create a new rack data.
@rack_router.post("/", response_model=dict)
async def create_rack_data(data: Racks, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"create_rack")
    query =None
    # check_role_access(current_user.role, [Roles.manager, Roles.director, Roles.admin])
    # Check if the specified zone (by ID) exists.
    query = {"_id":ObjectId(data.zone_id)}
    zone_data = await get_zone_by_id(query=query)
    data.rack_price +=zone_data["zone_price"]
    # Create a new rack based on the provided data.
    await create_rack(data=data.dict())
    # Return a success message.
    return {"success": "Successfully created rack data"}

# Endpoint to retrieve rack data by ID.
@rack_router.get("/{rack_id}", response_model=dict)
async def get_rack_data_by_id(rack_id: str, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    # check_role_access(current_user.role, [Roles.manager, Roles.director, Roles.admin])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_rack")
    # Get rack data by its ID.
    res = await get_rack_by_id(id=rack_id)
    # Return the retrieved rack data.
    return res

# Endpoint to retrieve all rack data.
@rack_router.get("/", response_model=Page[dict])
async def get_all_data_racks(current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    # check_role_access(current_user.role, [Roles.manager, Roles.admin, Roles.director])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_all_rack")
    query=None
    # Retrieve all rack data.
    results = await get_all_racks({})
    # Return a list of all rack data.
    return paginate(results)

# Endpoint to update rack data by ID.
@rack_router.put("/{rack_id}", response_model=dict)
async def update_rack_data_by_id(rack_id: str, data: RackUpdate, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    # check_role_access(current_user.role, [Roles.manager, Roles.admin, Roles.director])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"update_rack")
    query =None
    # Define the query to identify the rack by its ID.
    query = {"_id": ObjectId(rack_id)}
    # Convert RackUpdate data to a dictionary and update non-None values.
    data = data.dict()
    rack_d ={}
    for key, val in data.items():
        if val is not None and val !=0 and val !="string":
            rack_d[key] = val
    # Update the rack data.
    await update_racks(query=query, data=rack_d)
    # Return a success message.
    return {"success": "Successfully updated rack data"}

@rack_router.delete("/{rack_id}",response_model=dict)
async def delete_rack(rack_id:str,
                      current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"delete_rack")
    await delete_rack_by_id(rack_id)
    return {"success":f"successfully deleted rack by {rack_id}"}

@rack_router.get("/zone/{zone_id}",response_model=Page[dict])
async def get_all_racks_by_zone_id(zone_id:str,current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_all_rack")
    query=None
    racks = await get_all_racks(query={"zone_id":zone_id})
    return paginate(racks)

add_pagination(rack_router)

