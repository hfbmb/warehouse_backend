# Import necessary packages and modules
from bson.objectid import ObjectId
import time
from datetime import datetime

# Local packages and custom exceptions
from ..database import products_collection
from ..exceptions import (
    DoesNotExist,
    PermissionException,
)
from ..order.constants import Orders
from .constants import Products, Messages
from .models import ClientSideProduct
from ..user.constants import Users
from .exceptions import ProductAllReadyExist, ProductNotFoundById, ProductNotFoundByName

# Function to update product information by product ID
async def update_product(product_id: str, data: dict):
    result = await products_collection.update_one(
        {Products.id_: ObjectId(product_id), Products.deletionDate: {"$exists": False}},
        {"$set": data},
    )

    if not result.matched_count:
        raise ProductNotFoundById()

# Function to create or update a product
async def create_product(product_data: dict):
    existing_data = await products_collection.find_one({"_id": product_data["_id"]})
    if existing_data is None:
        # If a document with the specified _id does not exist, insert a new document
        await products_collection.insert_one(product_data)
    else:
        # If a document with the specified _id already exists, update its data
        await products_collection.replace_one(
            {"_id": product_data["_id"]}, product_data
        )

# Function to register a product
async def register_product(product: ClientSideProduct):
    data = product.dict()
    data[Products.status] = Messages.status_added
    data[Products.booking_date] = time.time() + 36000
    await products_collection.insert_one(data)

# Function to retrieve all products based on a query
async def return_all_products(query: dict) -> list:
    query[Products.deletionDate] = {"$exists": False}
    result = products_collection.find(query)
    documents = []
    async for doc in result:
        doc[Products.id] = str(doc.pop(Products.id_))
        documents.append(doc)
    return documents

# Function to get product information by product ID
async def get_product_by_id_(product_id: str):
    product = await products_collection.find_one(
        {Products.id_: ObjectId(product_id), Products.deletionDate: {"$exists": False}}
    )

    if not product:
        raise ProductNotFoundById()
    product[Products.id_] = str(product.pop(Products.id_))
    return product

# Function to update product quality verification
async def verification(product_id: str, passed_quality: bool):
    await products_collection.update_one(
        {Products.id: ObjectId(product_id)},
        {"$set": {Products.quality_check_passed: passed_quality}},
    )

# Function to update the product's storage location
async def confirmed_location(product_id: str, data: dict):
    await products_collection.update_one(
        {Products.id: ObjectId(product_id)}, {"$set": data}
    )

# Function to check if the current user has access to a product by product ID
async def check_access_product_by_worker_id(product_id: str, worker_id: str):
    result = await products_collection.find_one(
        {
            Products.id_: ObjectId(product_id),
            Products.warehouse_team + "." + Users.id: worker_id,
            Products.deletionDate: {"$exists": False},
        }
    )

    if not result:
        raise PermissionException

# Function to update multiple products by product IDs
async def update_many_products(products_id: list, data: dict):
    await products_collection.update_many(
        {"_id": {"$in": [ObjectId(_id) for _id in products_id]}},
        {"$set": data, "location_id": None},
    )

# Function to remove all products associated with a company
async def remove_all_products_in_company(company_name: str):
    query = {Products.deletionDate: datetime.utcnow()}

    result = await products_collection.update_many(
        {Products.company: company_name, Products.deletionDate: {"$exists": False}},
        {"$set": query},
    )

    if not result.matched_count:
        raise DoesNotExist

# Function to get the total quantity of a product by its name
async def get_total_quantity_product_by_name(product_name: str) -> dict:
    # Group products by name and calculate the total quantity
    pipeline = [
        {"$match": {"product_name": product_name}},
        {"$group": {"_id": "$product_name", "total_quantity": {"$sum": "$quantity"}}}
    ]
    result = await products_collection.aggregate(pipeline).to_list(None)
    if result:
        return {"product_name": result[0]["_id"], "total_quantity": result[0]["total_quantity"]}
    else:
        return {"product_name": product_name, "total_quantity": 0}

# Function to find products by client email
async def find_products_by_client_email(data: dict) -> list:
    product_list = []
    products = products_collection.find({"client_email": data["client_email"]})
    if products is None:
        raise DoesNotExist
    async for product in products:
        product["id"] = str(product.pop("_id"))
        product_list.append(product)
    return product_list

# Function to find a product by product name and client email
async def find_product_email(data: dict) -> dict:
    product = await products_collection.find_one(
        {"product_name": data["product_name"], "client_email": data["client_email"]})
    if product is None:
        raise DoesNotExist()
    product["id"] = str(product.pop("_id"))
    return product
