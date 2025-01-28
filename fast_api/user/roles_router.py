# Import necessary packages and modules
from fastapi import Depends, APIRouter, Cookie,HTTPException
from fastapi.responses import JSONResponse
from pydantic import Json
# from typing import Annotated, Optional
# from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page, paginate, add_pagination
from ..dependencies import get_current_user,user_has_permission
from .models import DBUser,Role,UpdateRole
from .constants import Roles
from .service import(
    create_role_for_users,
    get_role_by_id,
    update_role_by_data,
    get_all_roles_in_company,
    delete_role_by_id
)
# from .exception



role_router = APIRouter(prefix="/role",tags=["role"])

@role_router.post("/",response_model=dict)
async def create_role( 
                      data : Role,
                      current_user:DBUser =Depends(get_current_user)):
    # query ={
    #     "role_name":current_user.role,
    #     "company_name":current_user.company
    # }
    # await user_has_permission(query,"create_role")
    # check_role_access(current_user.role,[Roles.admin,Roles.director])
    data = data.dict()
    data["company_name"]=current_user.company
    await create_role_for_users(data)
    return {"success":"successfully created new role"}

@role_router.get("/",response_model=Page[dict])
async def get_all_role(current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_all_role")
    # check_role_access(current_user.role,[Roles.admin,Roles.director,Roles.manager])
    roles = await get_all_roles_in_company({"company_name":current_user.company})
    return paginate(roles)

@role_router.get("/{role_id}",response_model=dict)
async def get_role(role_id:str,current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"get_role")
    # check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.director])
    role = await get_role_by_id(id=role_id)
    return role

@role_router.put("/{role_id}",response_model=dict)
async def update_role(role_id:str,data:UpdateRole,
                      current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"update_role")
    data = data.dict()
    data.pop("permissions")
    role_d ={}
    for key,val in data.items():
        if val !=None and val !="string":
            role_d[key]=val
    # check_role_access(current_user.role,[Roles.admin,Roles.manager,Roles.director])
    await update_role_by_data(id=role_id,data=role_d)
    return {"success":"successfully updated role data"}

@role_router.delete("/{role_id}",response_model=dict)
async def delete_role(role_id:str,current_user:DBUser=Depends(get_current_user)):
    query ={
        "role_name":current_user.role,
        "company_name":current_user.company
    }
    await user_has_permission(query,"delete_role")
    await delete_role_by_id(id=role_id)
    return {"success":f"successfully deleted role by {role_id}"}

add_pagination(role_router)
