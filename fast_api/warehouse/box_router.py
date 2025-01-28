from fastapi import APIRouter, Depends
from bson.objectid import ObjectId
from fastapi_pagination import Page, paginate, add_pagination
from ..dependencies import (
    check_role_access,
    get_exception_responses,
    get_current_user,
    user_has_permission
)
from ..user.models import DBUser
from ..user.constants import Roles
from .models import Boxes,BoxesUpdate
from .service import (get_box_type_data_by_id,create_box_for_cell,
                      get_box_data_by_id,
                      get_all_boxes_data,
                      update_box_data,
                      current_user_warehouse,
                      delete_box_by_id)

box_router = APIRouter(prefix="/boxes",tags=["boxes"])

@box_router.post("/",response_model=dict)
async def create_box(data : Boxes,
                     current_user :DBUser = Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"create_box")
    # check_role_access(current_user.role,[Roles.manager,Roles.admin,Roles.director])
    warehouse_data = await current_user_warehouse({"company_name":current_user.company,
                                                   "warehouse_name":current_user.warehouse})
    type_data = await get_box_type_data_by_id(id=data.box_type_id)
    data = data.dict()
    data["length"]= type_data["type_length"]
    data["height"]= type_data["type_height"]
    data["width"]= type_data["type_width"]
    data["area"]=type_data["area"]
    data["volume"]=type_data["volume"]
    data["warehouse_id"]=warehouse_data["id"]
    await create_box_for_cell(data=data)
    return {"success":"successfully created box"}

@box_router.get("/{box_id}",response_model=dict)
async def get_box_by_id(box_id:str,
                        current_user:DBUser=Depends(get_current_user)):
    # check_role_access(current_user.role,
    #                   [Roles.manager,Roles.admin,Roles.director])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_box")
    box_data = await get_box_data_by_id(id=box_id)
    return box_data

@box_router.get("/",response_model=Page[dict])
async def get_all_box(current_user:DBUser = Depends(get_current_user)):
    # check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.director])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_all_box")
    warehouse_data = await current_user_warehouse({"company_name":current_user.company,
                                                   "warehouse_name":current_user.warehouse})
    boxes = await get_all_boxes_data(
        {"warehouse_id":warehouse_data["id"]})
    return paginate(boxes)

@box_router.put("/{box_id}",response_model=dict)
async def update_box(box_id:str,data:BoxesUpdate,
                     current_user:DBUser=Depends(get_current_user)):
    # check_role_access(current_user.role,[Roles.manager,Roles.admin,Roles.director])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"update_box")
    warehouse_data = await current_user_warehouse({"company_name":current_user.company,
                                                   "warehouse_name":current_user.warehouse})
    data = data.dict()
    box_d ={}
    for key,val in data.items():
        if val !=None and val !="string" and val !=0:
            box_d[key]=val
    await update_box_data(query={"_id":ObjectId(box_id),
                                 "warehouse_id":warehouse_data["id"]},data=box_d)
    return {"success":"succesfully updated box data"}

@box_router.delete("/{box_id}",response_model=dict)
async def delete_box(box_id:str,
                     current_user:DBUser = Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"delete_box")
    # check_role_access(current_user.role,
    #                   [Roles.admin,Roles.manager,Roles.director])
    await delete_box_by_id(id=box_id)
    return {"success":"successfully deleted box by id"}