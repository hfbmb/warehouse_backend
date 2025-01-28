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
# from .models import Boxes,BoxesUpdate

from .models import TypeBox,UpdateTypeBox
from .service import (
    get_box_type_data_by_id,
    create_box_type_data,
    delete_box_type_data_by_id,
    update_box_type_data,
    get_all_box_type_data,
    current_user_warehouse
)

type_router = APIRouter(prefix="/types",tags=["types"])

@type_router.post("/",response_model=dict)
async def create_type(data:TypeBox,
                      current_user:DBUser =Depends(get_current_user)):
    # check_role_access(current_user.role,[Roles.manager,Roles.admin,Roles.director])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"create_box")
    area = data.type_length * data.type_width
    volume = data.type_length * data.type_width*data.type_height
    data = data.dict()
    if current_user.role =="manager":
        warehouse_data = await current_user_warehouse({"company_name":current_user.company,
                                                   "warehouse_name":current_user.warehouse})
        data["warehouse_id"]= warehouse_data["id"]
    data["volume"]=volume
    data["area"]=area
    data["company_name"]= warehouse_data["company_name"]
    await create_box_type_data(data=data)
    return {"success":"succesfully created box_type"}


@type_router.get("/{type_id}",response_model=dict)
async def get_type_box_id(type_id:str,
                      current_user:DBUser= Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_box")
    # check_role_access(current_user.role,[Roles.manager,
    #                                      Roles.admin,
    #                                      Roles.controller,Roles.loader,
    #                                      Roles.warehouseman])
    type_data = await get_box_type_data_by_id(id=type_id)
    return type_data

@type_router.get("/",response_model=Page[dict])
async def get_all_box_type(current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_all_box")
    # check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.director])
    query =None
    if current_user.role ==Roles.admin :
        query ={}
    elif current_user.role ==Roles.manager:
        warehouse_data = await current_user_warehouse({"company_name":current_user.company,
                                                       "warehouse_name":current_user.warehouse})
        query ={"warehouse_id":warehouse_data["id"]}
    elif current_user.role==Roles.director:
        query={"company_name":current_user.company}
    box_types = await get_all_box_type_data(query=query)
    return paginate(box_types)

@type_router.delete("/{type_id}",response_model=dict)
async def delete_type_by_id(type_id:str,
                            current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"delete_box")
    # check_role_access(current_user.role,[Roles.manager,Roles.admin,Roles.director])
    await delete_box_type_data_by_id(id=type_id)
    return {"success":"successfully deleted box_type by id"}

@type_router.put("/{type_id}",response_model=dict)
async  def update_box_type(type_id:str,
                           data:UpdateTypeBox,
                           current_user:DBUser=Depends(get_current_user)):
    # check_role_access(current_user.role,
    #                   [Roles.admin,Roles.manager,Roles.director])
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"update_box")
    data = data.dict()
    type_d={}
    for key,val in data.items():
        if val !=None or val !=0:
            type_d[key]= val
    await update_box_type_data(query={"_id":ObjectId(type_id)},data=type_d)
    return {"success":"successfully updated type_box data"}

add_pagination(type_router)