from fastapi import APIRouter, Depends
from bson.objectid import ObjectId
from fastapi_pagination import Page, paginate, add_pagination
from ..dependencies import (
    check_role_access,
    get_exception_responses,
    get_current_user,
    user_has_permission
)
from .exceptions import LengthNotCorrectFloor,WidhtFloorNotCorrect
from ..user.models import DBUser
from ..user.constants import Roles
from .models import Floors, FloorUpdate
from .service import (get_all_floors, create_floor,
                       get_floor_by_id, delete_floor_by_id,
                      update_floors, get_rack_by_id)

# Create an APIRouter instance for warehouse-related operations.
floor_router = APIRouter(
    prefix="/floor", tags=["floor"]
)

# Endpoint to create a new floor.
@floor_router.post("/", response_model=dict)
async def create_floor_data(data: Floors, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    # check_role_access(current_user.role, [Roles.manager, Roles.admin, Roles.director])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"create_floor")
    # Check if the specified rack (by ID) exists.
    rack_data =await get_rack_by_id(id=data.rack_id)
    if data.floor_length !=0 and data.floor_length >rack_data["rack_length"]:
        raise LengthNotCorrectFloor
    if data.floor_width !=0 and data.floor_width >rack_data["rack_width"]:
        raise WidhtFloorNotCorrect
    if data.floor_length ==0:
        data.floor_length = rack_data["rack_length"]
    if data.floor_width ==0:
        data.floor_width = rack_data["rack_width"]
    data.floor_max_price +=rack_data["rack_price"]

    # Create a new floor based on the provided data.
    await create_floor(data=data.dict())
    # Return a success message.
    return {"success": "Successfully created floor data"}

# Endpoint to get floor data by its ID.
@floor_router.get("/{floor_id}", response_model=dict)
async def get_data_by_floorId(floor_id: str, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    # check_role_access(current_user.role, [Roles.manager, Roles.director, Roles.admin])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_floor")
    # Get floor data by its ID.
    res = await get_floor_by_id(id=floor_id)
    # Return the retrieved floor data.
    return res

# Endpoint to get all floor data.
@floor_router.get("/", response_model=Page[dict])
async def get_floors_data(current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_all_floor")
    # check_role_access(current_user.role, [Roles.manager, Roles.admin, Roles.director])
    # Retrieve all floor data.
    res = await get_all_floors({})
    # Return a list of all floor data.
    return paginate(res)

# Endpoint to update floor data by ID.
@floor_router.put("/{floor_id}", response_model=dict)
async def update_data_floor(floor_id: str, data: FloorUpdate, current_user: DBUser = Depends(get_current_user)):
    # Check if the current user has the required role for this action.
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"update_floor")
    query =None
    # check_role_access(current_user.role, [Roles.manager, Roles.director, Roles.admin])
    # Define the query to identify the floor by its ID.
    query = {"_id": ObjectId(floor_id)}
    data= data.dict()
    floor_d ={}
    for key,val in data.items():
        if val !=None and val !="string" and val !=0:
            floor_d[key]=val
    # Update the floor data with the provided values from FloorUpdate.
    await update_floors(query=query, data=floor_d)
    # Return a success message.
    return {"success": "Successfully updated floor data"}

@floor_router.delete("/{floor_id}",response_model=dict)
async def delete_floor(floor_id:str,current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"delete_floor")
    await delete_floor_by_id(id =floor_id)
    return {"success":f"successfully deleted floor by {floor_id}"}


@floor_router.get("/rack/{rack_id}",response_model=Page[dict])
async def get_floors_by_rack_id(rack_id:str,
                                current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_all_floor")
    query =None
    floors = await get_all_floors(query={"rack_id":rack_id})
    return paginate(floors)

add_pagination(floor_router)

