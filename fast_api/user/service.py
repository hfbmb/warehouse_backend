# Import necessary packages and modules
from bson.objectid import ObjectId
from datetime import datetime
from fastapi import HTTPException, status

# Import local packages and modules
from ..database import (
    users_collection, 
    companies_collection, temporary_tokens_collection,
    roles_collection,permissions_collection)
from ..utils import decode_access_token
from ..exceptions import (
    DuplicateKeyException,
    NotFoundException,
    InvalidCredentialsException,
    DoesNotExist,
    AlreadyExistsException,
    BaseAPIException,
    AlreadyAssignedException,
    EmployeeWorkStatus
)
from .exception import (
    UserAlreadyExist, UserNotFound,
    RolesNotFoundById,PermissionNotFoundById,RoleNotFoundByQuery)
from .models import DBUser, UserWithID, DBUserWithoutId
from .constants import Users
from ..company.constants import Company
from ..company.models import DeleteWarehouse
from ..order.constants import Orders
from .utils import create_refresh_token, create_access_token
from ..constants import Errors
from ..company.exception import CompanyNotFound

# Define an asynchronous function to check if a founder with a given email already exists
async def check_founder_exists(email):
    data = await users_collection.find_one({Users.email: email})
    if data:
        raise UserAlreadyExist()
    
async def custom_get_user_info_get(query:dict)->dict:
    user = await users_collection.find_one(query)
    if user:
        user["id"]= str(user.pop("_id"))
        return user
    else:
        raise UserNotFound
# Define an asynchronous function to register a founder user
async def register_founder(user: DBUserWithoutId):
    _id = await users_collection.insert_one(user.dict())
    return _id.inserted_id

# Define an asynchronous function to register a user
async def register_user_(user: dict):
    result = await companies_collection.find_one(
        {Company.company_name: user[Users.company]}
    )
    if not result:
        raise CompanyNotFound()

    # Register the user
    await users_collection.insert_one(user)

# Define an asynchronous function to update user data
async def update_user(user_id: str, data: dict):
    result = await users_collection.update_one(
        {Users.id_: ObjectId(user_id), Users.deletionDate: {"$exists": False}},
        {"$set": data},
    )
    if not result.modified_count:
        raise UserNotFound()

# Define an asynchronous function to get all users by company
async def get_all_users_by_company(company: str):
    users = users_collection.find(
        {Users.company: company, Users.deletionDate: {"$exists": False}}
    )
    if users is None:
        raise CompanyNotFound()
    users_list = []
    async for user in users:
        user[Users.id] = str(user.pop(Users.id_))
        users_list.append(user)

    return users_list

# Define an asynchronous function to get all users by warehouse
async def get_all_users_by_warehouse(company: str, warehouse: str):
    users = users_collection.find(
        {
            Users.company: company,
            Users.warehouse: warehouse,
            Users.deletionDate: {"$exists": False},
        }
    )
    if users is None:
        raise UserNotFound()
    users_list = []
    async for user in users:
        user[Users.id] = str(user.pop(Users.id_))
        users_list.append(user)

    return users_list

# Define an asynchronous function to get a user by a specific field and user data
async def get_user_by(field: str, user_data: str) -> DBUser:
    if field == Users.id_:
        user_data = ObjectId(user_data)
    user = await users_collection.find_one({field: user_data})
    if user is not None:
        if user.get(Users.deletionDate, 0):
            raise NotFoundException()
    else:
        raise InvalidCredentialsException
    user[Users.id] = str(user.pop(Users.id_))
    return DBUser(**user)

async def user_by_email(user_email:str)->dict:
    user_data = await users_collection.find_one({"email":user_email})
    if user_data is None:
        raise DoesNotExist()
    user_data["id"]=str(user_data.pop("_id"))
    return user_data




async def remove_user(user_id: str):
    query = {Users.deletionDate: datetime.utcnow()}
    user_id = ObjectId(user_id)
    result = await users_collection.update_one(
        {Users.id_: user_id, Users.deletionDate: {"$exists": False}}, {"$set": query}
    )
    if not result.matched_count:
        raise UserNotFound()

# Define an asynchronous function to remove all users in a company
async def remove_all_user_in_company(company_name: str):
    query = {Users.deletionDate: datetime.utcnow()}
    result = await users_collection.update_many(
        {Users.company: company_name, Users.deletionDate: {"$exists": False}},
        {"$set": query},
    )
    if not result.matched_count:
        raise DoesNotExist

# Define an asynchronous function to remove all users in a warehouse
async def remove_all_users_in_warehouse(query: DeleteWarehouse):
    set_query = {Users.deletionDate: datetime.utcnow()}
    result = await users_collection.update_many(
        {
            Users.company: query.company_name,
            Users.warehouse: query.warehouse_name,
            Users.deletionDate: {"$exists": False},
        },
        {"$set": set_query},
    )
    if not result.matched_count:
        raise UserNotFound()

# Define an asynchronous function to change a user's password
async def change_password_(username, hashed_password):
    request = await users_collection.update_one(
        {Users.email: username, Users.deletionDate: {"$exists": False}},
        {"$set": {Users.hashed_password: hashed_password}},
    )
    if not request.matched_count:
        raise InvalidCredentialsException

# Define an asynchronous function to add an order to multiple users
async def add_order_to_users(order: dict, users: list[UserWithID]):
    user_ids = [ObjectId(user[Users.id]) for user in users]

    result = await users_collection.update_many(
        {Users.id_: {"$in": user_ids}, Users.deletionDate: {"$exists": False}},
        {"$push": {Users.orders: order}},
    )
    if not result.matched_count:
        raise UserNotFound()
    if not result.modified_count:
        raise AlreadyExistsException

# Define an asynchronous function to add an order to a salesman
async def add_order_to_salesman(salesman_id: str, order_id: str):
    result = await users_collection.update_one(
        {Users.id_: ObjectId(salesman_id), Users.deletionDate: {"$exists": False}},
        {"$set": {Users.order_id: order_id}},
    )

    if not result.matched_count:
        raise UserNotFound()
    if not result.modified_count:
        raise AlreadyExistsException

# Define an asynchronous function to start user work on an order
async def start_user_work(order_id: str, user_id: str, date: datetime):
    update_result = await users_collection.update_one(
        {
            Users.id_: ObjectId(user_id),
            Users.deletionDate: {"$exists": False},
            Users.orders + "." + Users.order_id: order_id,
        },
        {"$set": {"orders.$.status": "started", "orders.$.start_time": date}},
    )
    if not update_result.matched_count:
        raise UserNotFound()

# Define an asynchronous function to end user work on an order
async def end_user_work(order_id: str, user_id: str, status: str):
    date = datetime.now()
    update_result = await users_collection.update_one(
        {Users.id_: ObjectId(user_id), Users.orders + "." + Users.order_id: order_id},
        {"$set": {"orders.$.status": status, "orders.$.end_time": date}},
    )
    if not update_result.matched_count:
        raise UserNotFound()

# Define an asynchronous function to check the schedule of employees for order assignment
async def check_employee_schedule(data: dict):
    try:
        employees_busy = []
        users = users_collection.find(
            {
                Users.id_: {"$in": data[Orders.warehouse_team]},
                Users.orders: {"$exists": True},
                Users.deletionDate: {"$exists": False},
            }
        )
        async for user in users:
            for order in user[Users.orders]:
                if order[Orders.status] != "finished":
                    if not (
                        (
                            order[Orders.end_schedule] < data[Orders.initial_schedule]
                            and order[Orders.end_time] < data[Orders.initial_time]
                        )
                        or (
                            order[Orders.initial_schedule] < data[Orders.end_schedule]
                            and order[Orders.initial_time] < data[Orders.end_schedule]
                        )
                    ):
                        employees_busy.append(user)
    except BaseAPIException as e:
        raise e
    if len(employees_busy):
        raise AlreadyAssignedException(busy_employees=employees_busy)

# Define an asynchronous function to check the work status of a user for an order
async def check_user_status_for_order(user_id: str, order_id: str):
    count = await users_collection.count_documents(
        {
            Users.id_: ObjectId(user_id),
            Users.orders + "." + Users.order_id: order_id,
            Users.orders + "." + Orders.status: "started",
        }
    )
    if count != 1:
        raise EmployeeWorkStatus

# Define an asynchronous function to get users associated with an order by order ID
async def users_by_order_id(order_id: str):
    users_data = []
    cursor = users_collection.find(
        {
            Users.orders + "." + Users.order_id: order_id,
            Users.deletionDate: {"$exists": False},
        }
    )
    async for user in cursor:
        user[Users.id] = str(user.pop(Users.id_))
        users_data.append(user)
    if not users_data:
        raise UserNotFound()
    return users_data

# Define an asynchronous function to refresh a new access token using a refresh token
async def refresh_new_access_token(refresh_token: str) -> dict:
    token = await temporary_tokens_collection.find_one({"refresh_token": refresh_token})
    if not token:
        raise DoesNotExist("refresh_token")
    # Get the Refresh token in string format from the database
    refresh_token_str = token.get("refresh_token")
    decoded_token = decode_access_token(refresh_token_str)
    if decoded_token is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.invalid_token)
    access_token = await create_access_token(decoded_token["user_id"])
    rtk = refresh_token_str
    tokens = {
        "access_token": access_token,
        "refresh_token": rtk
    }
    return tokens


async def update_user_order_status(user_id:str,order_data:dict):
    res = await users_collection.update_one(
        {"_id":ObjectId(user_id),
        Users.orders + "." + Users.order_id: order_data["order_id"]},
        {"$set":{Users.orders + "." + Orders.status:order_data["status"]}})
    if res.matched_count >0:
        pass
    else:
        raise UserNotFound
    




####All functions for roles and permissions

async def create_role_for_users(role_data:dict):
    result = await roles_collection.insert_one(role_data)
    if result.inserted_id:
        pass
    else:
        raise Exception("error in the create role")

async def get_role_by_id(id:str)->dict:
    result = await roles_collection.find_one({"_id":ObjectId(id)})
    if result:
        result["id"]= str(result.pop("_id"))
        return result
    else:
        raise RolesNotFoundById
    
async def get_all_roles_in_company(query:dict)->list:
    result =[]
    roles = roles_collection.find(query)
    # if roles is None :
    #     raise RoleNotFoundByQuery
    async for rol in roles:
        rol["id"]=str(rol.pop("_id"))
        result.append(rol)
    return result

async def delete_role_by_id(id:str):
    res = await roles_collection.delete_one({"_id":ObjectId(id)})
    if res.deleted_count>0:
        pass
    else:
        raise RolesNotFoundById
    
async def update_role_by_data(id:str,data:dict):
    result = await roles_collection.update_one({"_id":ObjectId(id)},{"$set":data})
    if result.matched_count >0:
        pass
    else:
        raise RolesNotFoundById

####This functions for permissions
async def create_permission(data:dict):
    result = await permissions_collection.insert_one(data)
    if result.inserted_id:
        pass
    else:
        raise Exception("error in permission create")

async def get_permission_by_id(id:str)->dict:
    result = await permissions_collection.find_one({"_id":ObjectId(id)})
    if result:
        result["id"]=str(result.pop("id"))
        return result
    else:
        raise PermissionNotFoundById
    
async def get_all_permission_data(query:dict)->list:
    permissions =[]
    result = permissions_collection.find(query)
    async for per in result:
        per["id"]=str(per.pop("_id"))
        permissions.append(per)

    return permissions

async def update_permission_by_id(id:str,data:dict):
    result = await permissions_collection.update_one({"_id":ObjectId(id)},{"$set":data})
    if result.matched_count>0:
        pass
    else:
        raise PermissionNotFoundById
    
async def delete_permission_by_id(id:str):
    res = await permissions_collection.delete_one({"_id":ObjectId(id)})
    if res.deleted_count>0:
        pass
    else:
        raise PermissionNotFoundById