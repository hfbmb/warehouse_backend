# Import necessary packages and modules
from fastapi import Depends, APIRouter, Cookie,HTTPException
from fastapi.responses import JSONResponse
from pydantic import Json
from fastapi_pagination import Page, paginate, add_pagination
from ..dependencies import get_current_user,check_role_access,user_has_permission
from .models import DBUser,Permission,UpdatePermission
from .constants import Roles
from .service import (create_permission,get_all_permission_data,
                      get_permission_by_id,update_permission_by_id,
                      delete_permission_by_id)


permission_router = APIRouter(prefix="/permission",tags=["permission"])

@permission_router.post("/",response_model=dict)
async def create_permision(data:Permission,current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="create_permission")
    # check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.director])
    await create_permission(data=data.dict())
    return {"success":"successfully created permission data"}

@permission_router.get("/",response_model=Page[dict])
async def get_all_permission(current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="get_all_permission")
    # check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.director])
    permissions = await get_all_permission_data({})
    return paginate(permissions)

@permission_router.get("/{permission_id}",response_model=dict)
async def get_permission_data(permission_id:str,
                              current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="get_permission")
    permission = await get_permission_by_id(id=permission_id)
    return permission

@permission_router.put("/{permission_id}",response_model=dict)
async def update_permission(permission_id:str,
                            data :UpdatePermission,
                            current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query=query,required_permission="update_permission")
    data =data.dict()
    per_dict ={}
    for key,val in data.items():
        if val !=None and val !="string":
            per_dict[key]=val
    # check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.director])
    await update_permission_by_id(id=permission_id,data=per_dict)
    return {"success":"successfully updated permission data"}

@permission_router.delete("/{permission_id}",response_model=dict)
async def delete_permission(permission_id:str,current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"delete_permission")
    await delete_permission_by_id(id=permission_id)
    return {"success":f"successfully deleted permission by {permission_id}"}

add_pagination(permission_router)