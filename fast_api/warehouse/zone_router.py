from fastapi import APIRouter,Depends
from bson.objectid import ObjectId
from fastapi_pagination import Page, paginate, add_pagination
from ..dependencies import (
    check_role_access,
    get_exception_responses,
    user_has_permission,
    get_current_user,
)
from ..user.models import DBUser
from ..user.constants import Roles
from .models import Zones,ZoneById,ZoneUpdate
from .service import (create_zone,
                      get_zone_by_id,
                      delete_zone,
                      update_zone,
                      get_all_zones,
                      check_category_by_id)

# Create an APIRouter instance for warehouse-related operations.
zone_router = APIRouter(
    prefix="/zone", tags=["zone"]
)

@zone_router.post("/",response_model=dict)
async def creat_zone_for_category(zone_data:Zones,
                                  current_user : DBUser= Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"create_zone")
    # check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.director])
    zone_data = zone_data.dict()
    await check_category_by_id(id=zone_data["category_id"])
    await create_zone(zone_data)
    return {"success":"successfully created zone"}

@zone_router.get("/{zone_id}",response_model=ZoneById)
async def get_zone_data_by_id(zone_id:str,
                         current_user:DBUser =Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_zone")
    # check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.director])
    res =await get_zone_by_id({"_id":ObjectId(zone_id)})
    return ZoneById(**res)
    
@zone_router.get("/",response_model=Page[dict])
async def get_all_zones_data(current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_all_zone")
    # check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.director])
    res = await get_all_zones({})
    return paginate(res)

@zone_router.put("/{zone_id}",response_model=dict)
async def update_data_buy_order_id(zone_id:str,zone_data:ZoneUpdate,
                                   current_user:DBUser=Depends(get_current_user)):
    # check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.director])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"update_zone")
    zone_data = zone_data.dict()
    data ={}
    for key,val in zone_data.items():
        if val is not None and val !="string" and val !=0:
            data[key]=val
    await update_zone({"_id":ObjectId(zone_id)},data)
    return {"success":"successfully updated zone data"}

@zone_router.delete("/{zone_id}",response_model=dict)
async def delete_zone_by_id(zone_id:str,
                      current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"delete_zone")
    await delete_zone({"_id":ObjectId(zone_id)})
    return {"success":f"successfully deleted zone by {zone_id}"}

@zone_router.get("/category/{category_id}",response_model=Page[dict])
async def get_all_zones_by_category_id(category_id:str,current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_all_zone")
    query =None
    query ={
        "category_id":category_id
    }
    zones = await get_all_zones(query=query)
    return paginate(zones)

add_pagination(zone_router)