from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from .utils import password_validation
import re
from fastapi import UploadFile, File
from datetime import datetime,timedelta
from ..company.models import Address
from .constants import Users
import time

class ForgotPassword(BaseModel):
    verification_code: int = Field(...,description="verification code")
    email : EmailStr 
    new_password: str = Field(...,description="new parol for ")
    @field_validator("new_password")
    @classmethod
    def validate_password(cls, passwd):
        return password_validation(passwd)
    
    class Config:
        json_schema_extra={
            "example":{
                "verification_code": 123456,   ## Replace with the actual verification code sent to the user
                "email": "user@example.com",   ## User's email address
                "new_password": "NewSecurePassword123"  ## The new password for the user
            }
        }

class User(BaseModel):
    firstname: str = Field(..., description="firstname of a user", max_length=100)
    lastname: str = Field(..., description="lastname of a user", max_length=100)
    email: EmailStr = Field(..., description="email of the user")
    telephone: str = Field(..., description="telephone number of the user")
    vacation: datetime = Field(
        default=datetime.now() + timedelta(days=365),
        description="vacation date of the user (default: current date + 1 year)"
    )
    is_confirmed:Optional[bool]=Field(default=False,description="default status of user")
    verification_code : int =Field(default=None,description="code of user")
    start_time: Optional[str] = Field(default=time.strftime("%H:%M"), description="business time start")
    end_time: Optional[str] = Field(
        default=(datetime.now() + timedelta(hours=10)).strftime("%H:%M"),
        description="business end time (current time + 10 hours)"
    )
    def get_start_time_struct_time(self):
        return time.strptime(self.start_time, "%H:%M")
    def get_end_time_struct_time(self):
        return time.strptime(self.end_time, "%H:%M")
    user_address : Optional[Address] = Field(None,description="user address")
    # @field_validator("telephone")
    # @classmethod
    # def validate_phone_number(cls, phone_number):
    #     pattern = re.compile(
    #         r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}"
    #     )
    #     match = re.search(pattern, phone_number)
    #     if not match:
    #         raise ValueError("Invalid phone number")
    #     return phone_number
    class Config:
        json_schema_extra={
            "example":{
                "firstname": "John",
                "lastname": "Doe",
                "email": "john.doe@example.com",
                "telephone": "123-456-7890",
                "vacation": "2023-10-18T06:28:08.834Z",
                "is_confirmed": True,
                "start_time": "08:00",
                "end_time": "18:00",
                "user_address": {
                    "zip_code": "12345",
                    "street": "123 Main St",
                    "city": "Anytown",
                    "region": "Someregion",
                    "country": "Somecountry"
                }
            }
        }


class Worker(User):
    role: str = Field(
        ...,
        description="There are different roles in this platform: Admin, Q/A manager, Worker",
        max_length=50,
    )
    warehouse: Optional[str] = Field(
        None, description="Name of worker's warehouse", max_length=100
    )

    class Config:
        json_schema_extra ={
            "example":{
                "firstname": "Alice",
                "lastname": "Smith",
                "email": "alice.smith@example.com",
                "telephone": "987-654-3210",
                "vacation": "2023-10-18T06:28:08.834Z",
                "is_confirmed": True,
                "start_time": "09:00",
                "end_time": "17:00",
                "user_address": {
                    "zip_code": "54321",
                    "street": "456 Elm St",
                    "city": "Worker City",
                    "region": "Workerville",
                    "country": "Workland"
                },
                "role": "Worker",
                "warehouse": "Warehouse 1"
            }
        }


class WebUser(Worker):
    password: str = Field(..., description="User's password")

    @field_validator("password")
    @classmethod
    def validate_password(cls, passwd):
        return password_validation(passwd)

    class Config:
        json_schema_extra = {
            "example": {
                "firstname": "John",
                "lastname": "Dwain",
                "email": "johnd@example.com",
                "telephone": "+7 (708) 156-35-84",
                # "vacation":None,
                "role": "salesman",
                "warehouse": "Name or None",
                "password": "John@1234",
                Users.user_address:{
                    Users.zip_code:"zip_code",
                    Users.street:"street",
                    Users.city:"Astana",
                    Users.country:"Qazaqstan",
                    Users.region:"Aqmola"
                }                
            }
        }


class ImageCreate(BaseModel):
    file: UploadFile = File(...)


class WebFounder(User):
    # role : str = Field(...,description="role id of director")
    password: str = Field(..., description="Founder's password")

    @field_validator("password")
    @classmethod
    def validate_password(cls, passwd):
        return password_validation(passwd)

    class Config:
        json_schema_extra = {
            "example": {
                "firstname": "John",
                "lastname": "Dwain",
                "email": "johnd@example.com",
                "telephone": "+7 (708) 156-35-84",
                "vacation":None,
                "password": "asdASD123#",
                # "role":"12dweewqw",
                Users.user_address:{
                    Users.zip_code:"zip_code",
                    Users.street:"street",
                    Users.city:"Astana",
                    Users.country:"Qazaqstan",
                    Users.region:"Aqmola"
                }
            }
        }


class UserOut(Worker):
    company: str = Field(..., description="Name of user's company", max_length=100)


class UserWithID(UserOut):
    id: str = Field(..., description="Id of a user", max_length=100)


class DBUserWithoutId(UserOut):
    hashed_password: str = Field(..., description="hash of the password")


class DBUser(UserOut):
    id: str = Field(..., description="Id of user")
    hashed_password: str = Field(..., description="hash of the password")


class UserChangePassword(BaseModel):
    email: str = Field(..., description="firstname of a user", max_length=100)
    old_password: str = Field(..., description="the current password of user")
    new_password: str = Field(..., description="the new password of user")

    @field_validator("old_password", "new_password")
    @classmethod
    def validate_password(cls, passwd):
        return password_validation(passwd)


class UserUpdate(BaseModel):
    class Config:
        extra = "allow"


class RolePermissionId(BaseModel):
    permission_name:str =Field(...,description="permission id")

class Role(BaseModel):
    role_name:str =Field(...,description="role name")
    # company_name: str = Field(...,description="company name")
    permissions : Optional[list[RolePermissionId]]=Field(default=None,description="list of permissions")
    class Config:
        json_schema_extra = {
            "example":{
                "role_name":"director",
                "permissions":[
                    {"permission_name": "view_all_users"},         
                    {"permission_name": "view_user_by_id"},        
                    {"permission_name": "register_user"},          
                    # {"permission_name": "confirm_verification"},   
                    # {"permission_name": "refresh_token"},          
                    {"permission_name": "delete_user"},            
                    # {"permission_name": "reset_password"},         
                    # {"permission_name": "reset_password_with_code"},
                    {"permission_name": "update_user_data"},
                    {"permission_name": "view_own_company"},
                    {"permission_name": "create_company"},
                    {"permission_name": "update_company_data"},
                    {"permission_name": "delete_company"},
                    ###Role_user
                    {"permission_name":"create_role"},
                    {"permission_name":"get_all_role"},
                    {"permission_name":"get_role"},
                    {"permission_name":"update_role"},
                    {"permission_name":"delete_role"},
                    ####Permission_for_user
                    {"permission_name":"create_permission"},
                    {"permission_name":"get_all_permission"},
                    {"permission_name":"get_permission"},
                    {"permission_name":"update_permission"},
                    {"permission_name":"delete_permission"},
                    ###Order permissions
                    {"permission_name": "view_order_team"},
                    {"permission_name":"create_sub_order"},
                    {"permission_name":"delete_main_order"},
                    # {"permission_name": "start_work_on_order"},
                    {"permission_name": "view_all_orders"},
                    # {"permission_name": "view_order_details"},
                    {"permission_name": "generate_sales_url"},
                    {"permission_name": "generate_order_update_url"},
                    {"permission_name": "view_unchecked_products"},
                    {"permission_name": "create_order"},
                    {"permission_name": "update_order"},
                    {"permission_name": "record_sales_info"},
                    {"permission_name": "create_invoice"},
                    {"permission_name": "approve_order_products"},
                    {"permission_name": "update_order_status"},
                    #products router
                    {"permission_name": "get_product_by_client_email"},
                    {"permission_name": "generate_qr_code"},
                    {"permission_name": "get_all_products"},
                    {"permission_name": "get_products_by_orderID"},
                    {"permission_name": "get_product_info"},
                    {"permission_name": "relocate_product"},
                    {"permission_name": "get_product_by_name"},
                    ##warehouse
                    {"permission_name": "view_own_warehouse"},
                    {"permission_name": "view_all_warehouses"},
                    {"permission_name": "view_warehouse_by_id"},
                    {"permission_name": "view_warehouse_users"},
                    {"permission_name": "add_warehouse"},
                    {"permission_name": "update_warehouse"},
                    {"permission_name": "delete_warehouse"},
                    {"permission_name": "delete_gate"},
                    ####Zone permission
                    {"permission_name":"create_zone"},
                    {"permission_name":"get_all_zone"},
                    {"permission_name":"get_zone"},
                    {"permission_name":"update_zone"},
                    {"permission_name":"delete_zone"},
                    ####box permission
                    {"permission_name":"create_box"},
                    {"permission_name":"get_all_box"},
                    {"permission_name":"get_box"},
                    {"permission_name":"update_box"},
                    {"permission_name":"delete_box"},
                    ####Rack permission
                    {"permission_name":"create_rack"},
                    {"permission_name":"get_all_rack"},
                    {"permission_name":"get_rack"},
                    {"permission_name":"update_rack"},
                    {"permission_name":"delete_rack"},
                    ###floor permission
                    {"permission_name":"create_floor"},
                    {"permission_name":"get_all_floor"},
                    {"permission_name":"get_floor"},
                    {"permission_name":"update_floor"},
                    {"permission_name":"delete_floor"},
                    ###cell permission
                    {"permission_name":"create_cell"},
                    {"permission_name":"get_all_cell"},
                    {"permission_name":"get_cell"},
                    {"permission_name":"update_cell"},
                    {"permission_name":"delete_cell"},
                    ###Category permission
                    {"permission_name":"create_category"},
                    {"permission_name":"get_all_category"},
                    {"permission_name":"get_category"},
                    {"permission_name":"update_category"},
                    {"permission_name":"delete_category"},
                    ###Report permissions
                    {"permission_name": "view_reports"},
                    {"permission_name": "check_order_documents"},
                    {"permission_name": "check_packaging"},
                    {"permission_name": "check_product_arrival"},
                    {"permission_name":"check_quality"},
                    {"permission_name":"allocate_warehouse"},
                    {"permission_name":"confirm_location"},
                    {"permission_name":"unalocate_product"},
                    {"permission_name":"send_to_customer"},
                ]
            }
        }

class UpdateRole(BaseModel):
    role_name:str =Field(None,description="role name")
    company_name: str = Field(None,description="company name")
    permissions : Optional[list[RolePermissionId]]=Field(default=None,description="list of permissions")


class Permission(BaseModel):
    permission_name:str =Field(...,description="permission name")

class UpdatePermission(BaseModel):
    permission_name:str =Field(default=None,description="permission name")