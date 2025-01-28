# Installed packages
from fastapi import HTTPException
import time, logging
from bson.objectid import ObjectId
from datetime import datetime

# Local packages
from ..database import orders_collection, temporary_tokens_collection
from ..exceptions import (
    DoesNotExist,
    AlreadyExistsException,
    PermissionException,
    TokenInvalidException,
    LogicBrokenException,
    DoesntMatchStatus
)
from .exception import OrderNotFoundById,NoProductInOrder
from .constants import Orders, Messages
from .models import Order
from ..product.constants import Products, Messages as ProdMessages
from ..user.constants import Users, Roles


# ###Function to create all sub_orders 
# async def create_sub_orders(main_order_id:str,orders:list):
#     res = orders_collection.insert_many(orders)

# Function to return all orders based on user role and access rights.
async def return_all_orders(user_id: str, role: str, company: str, warehouse: str):
    query = {}
    # Define the query based on the user's role and access rights.
    if role == Roles.salesman:
        query[Orders.salesman_id] = user_id
    elif role == Roles.admin or role == Roles.director:
        query[Orders.recipient] = company
    else:
        query[Orders.warehouse] = warehouse
        if role != Roles.manager:
            query[Orders.warehouse_team + "." + Users.id] = user_id
    # Exclude orders marked for deletion.
    query[Orders.deletionDate] = {"$exists": False} 
    orders = []
    cursor = orders_collection.find(query)
    # Convert cursor results to a list of orders.
    for order in await cursor.to_list(None):
        order[Users.id] = str(order.pop(Users.id_))
        orders.append(order)
    return orders

# Function to get an order by its ID.
async def get_order_by_id(order_id: str) -> dict:
    order = await orders_collection.find_one(
        {Orders.id: ObjectId(order_id), Orders.deletionDate: {"$exists": False}}
    )
    if not order:
        raise OrderNotFoundById()
    order.pop(Orders.id)
    return order

# Function to register a new order and return its ID.
async def register_order(order: dict) -> str:
    result = await orders_collection.insert_one(order)
    return str(result.inserted_id)

# Function to update the status of an order.
async def update_order_status(order_id: str, status: str):
    update_result = await orders_collection.update_one(
        {Orders.id: ObjectId(order_id), Orders.deletionDate: {"$exists": False}},
        {"$set": {Orders.status: status}},
    )

    if not update_result:
        raise OrderNotFoundById()

# Function to update order invoice details.
async def update_order_invoice(order_id: str, data):
    result = await orders_collection.update_one(
        {Orders.id: ObjectId(order_id), Orders.deletionDate: {"$exists": False}},
        {"$set": data},
    )
    if not result.matched_count:
        raise OrderNotFoundById()
    if not result.modified_count:
        raise AlreadyExistsException

# Function to update the status of a specific product within an order.
async def update_order_product_status(order_id: str, product_name: str, status: str):
    result = await orders_collection.update_one(
        {
            "_id": ObjectId(order_id),
            "products.product_name": product_name
        },
        {"$set": {"products.$.status": status}},
    )
    if result.modified_count == 0:
        logging.error("update order product status err")
        raise OrderNotFoundById()

# Function to retrieve non-checked products within an order based on their status.
async def get_order_products_filtered_by_status(order_id: str) -> list[dict]:
    result = await orders_collection.find_one(
        {Orders.id: ObjectId(order_id), Orders.deletionDate: {"$exists": False}},
        {Orders.products: 1, Orders.id: 0},
    )
    if not result:
        raise OrderNotFoundById()
    products = result.get(Orders.products)
    non_checked_products = []
    # Filter products by their status.
    for product in products:
        if product.get(Products.status) != ProdMessages.status_approved:
            non_checked_products.append(product)
    return non_checked_products
# Function to find a product within an order by its name.
async def find_product_by_name(order_id: str, product_name: str):
    order_data = await orders_collection.find_one({Orders.id: ObjectId(order_id)})
    
    if order_data is None:
        raise OrderNotFoundById()
    
    product_result = None
    
    for product in order_data[Orders.products]:
        if product[Products.product_name] == product_name:
            # Add order-specific information to the product data.
            product[Products.order_id] = str(order_data[Orders.id])
            product[Products.company] = order_data[Orders.recipient]
            product[Products.warehouse] = order_data[Orders.warehouse]
            product[Products.initial_schedule] = order_data[Orders.initial_schedule]
            product[Products.end_schedule] = order_data[Orders.end_schedule]
            product[Products.place] = order_data[Orders.place]
            product[Products.initial_time] = order_data[Orders.initial_time]
            product[Products.end_time] = order_data[Orders.end_time]
            product[Products.warehouse_team] = order_data[Orders.warehouse_team]
            product[Products.date_of_arrival] = time.time()
            product_result = product
    
    if not product_result:
        raise NoProductInOrder()
    
    return product_result

# Function to create a temporary token for salesmen.
async def create_token(token: str, salesman_id: str, created_at) -> None:
    await temporary_tokens_collection.insert_one(
        {"token": token, "salesman_id": salesman_id, "createdAt": created_at}
    )

# Function to validate a token and retrieve the associated salesman's ID.
async def validate_token_and_get_salesman_id(token: str) -> str:
    doc = await temporary_tokens_collection.find_one({"token": token})
    
    if not doc:
        raise TokenInvalidException
    
    return doc["salesman_id"]

# Function to delete a temporary token.
async def delete_token(token: str):
    await temporary_tokens_collection.delete_one({"token": token})

# Function to update an order with new data.
async def update_order(order_id: str, data: dict):
    result = await orders_collection.update_one(
        {Orders.id: ObjectId(order_id)}, {"$set": data}
    )
    
    if not result.matched_count:
        raise OrderNotFoundById
    
    if not result.modified_count:
        raise AlreadyExistsException

# Function to check if a user has access to a specific order based on a query.
async def check_access_order_by_employee_id(query: dict):
    query[Orders.deletionDate] = {"$exists": False}
    result = await orders_collection.find_one(query)
    
    if not result:
        raise PermissionException

# Function to mark all orders from a specific company as deleted.
async def remove_all_orders_in_company(company_name: str):
    query = {Orders.deletionDate: datetime.utcnow()}
    result = await orders_collection.update_many(
        {Orders.recipient: company_name, Orders.deletionDate: {"$exists": False}},
        {"$set": query},
    )
    
    if not result.matched_count:
        raise DoesNotExist

# Function to check if a salesman has already recorded an order.
async def check_salesman_record_repetition(order_id: str):
    result = await orders_collection.find_one({Orders.id: ObjectId(order_id)})
    
    if not result:
        raise DoesNotExist
    
    if result[Orders.status] == Messages.status_salesman_recorded:
        raise AlreadyExistsException

# Function to check the coherence of order status transitions.
async def check_coherence(data: dict):
    result = await orders_collection.find_one(
        {Orders.id: ObjectId(data[Orders.id]), Orders.deletionDate: {"$exists": False}}
    )

    sequential_order = {
        Messages.st_or_added: 1,
        Messages.status_salesman_recorded: 2,
        Messages.status_invoiced: 3,
        Messages.status_approve: 4,
        Messages.status_failed: 4,
    }
    if not result:
        raise DoesNotExist
    if result[Orders.status] == data[Orders.status]:
        raise AlreadyExistsException
    if (
        sequential_order[data[Orders.status]] - sequential_order[result[Orders.status]]
        != 1
    ):
        raise LogicBrokenException

# Function to validate that two salesman IDs match.
async def validate_salesman(salesman_id_1, salesman_id_2):
    if salesman_id_1 != salesman_id_2:
        raise PermissionException

# Function to check if the order status matches the expected status.
async def check_order_status(order_id: str, status: str):
    order_data = await orders_collection.find_one({"_id": ObjectId(order_id)})  
    if order_data is None:
        logging.error("not found order by id")
        raise OrderNotFoundById
    elif order_data["status"] != status:
        raise HTTPException(status_code=403, detail=f"order status not equal {status}")
    else:
        pass



async def check_order_product_status(products:list,status:str)->str:
    for product in products:
        if product["status"]!=status:
            raise DoesntMatchStatus
    return "ok"


async def get_all_sub_orders(query:dict)->list:
    orders = orders_collection.find(query)
    if orders is None:
        raise OrderNotFoundById
    sub_orders =[]
    async for order in orders:
        order["id"]=str(order.pop("_id"))
        sub_orders.append(order)
    return sub_orders
    

async def delete_order_by_order_id(query:dict):
    res = await orders_collection.delete_one(query)
    if res.deleted_count>0:
        pass
    else:
        raise OrderNotFoundById
