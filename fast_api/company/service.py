# Import necessary packages and modules
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from fastapi import HTTPException, status
import datetime
import logging

# Import local packages and modules
from ..database import (
    companies_collection,
    users_collection,
    temporary_locations,
    locations_collection,
    unsuitable_collection,
    spoilages_collection,
)
from .models import ReturnCompany, CompanyWithStatus, DeleteWarehouse
from .exception import(
    CompanyAlredyExist,
    CompanyNotFound,WarehouseNotFound
)
from ..exceptions import (
    DoesNotExist,
)
from . import constants
from ..product.constants import Products
from ..report.constants import Reports

# Configure logging
logger = logging.getLogger("company_service")
logger.setLevel(logging.DEBUG)
# Function to check if a company with the given name already exists
async def check_company_exists(company_name):
    data = await companies_collection.find_one(
        {constants.Company.company_name: company_name}
    )
    if data:
        logger.error(f"Duplicate key error: Company {company_name} already exists.")
        raise CompanyAlredyExist()

# Function to check if a warehouse exists within a company
async def warehouse_exists(company: str, warehouse: str):
    query = {
        constants.Company.company_name: company,
        constants.Company.warehouses
        + "."
        + constants.Warehouses.warehouse_name: warehouse,
    }
    data = await companies_collection.find_one(query)
    return data

# Function to create a new company with status
async def create_company_(data: CompanyWithStatus):
    _id =await companies_collection.insert_one(data.dict())
    return _id.inserted_id

# Function to retrieve company data by name
async def get_company(name: str) -> ReturnCompany:
    data = await companies_collection.find_one(
        {
            constants.Company.company_name: name,
            constants.Company.deletionDate: {"$exists": False},
        }
    )
    if not data:
        logger.error(f"Company {name} not found.")
        raise CompanyNotFound()
    data[constants.Company.id] = str(data.pop(constants.Company.id_))
    return data

# Function to check if a company or warehouse exists for order-related queries
async def check_order_company_and_or_warehouse(query: dict):
    query[constants.Company.deletionDate] = {"$exists": False}
    result = await companies_collection.find_one(query)

    if not result:
        logger.error("Data not found")
        raise CompanyNotFound
    else:
        pass

# Function to update company data
async def update_data(name: str, data: dict):
    try:
        result = await companies_collection.update_one(
            {
                constants.Company.company_name: name,
                constants.Company.deletionDate: {"$exists": False},
            },
            {"$set": data},
        )
        if result.modified_count == 0:
            logger.warning(f"No records modified for company {name}.")
            raise CompanyNotFound()
        if (
            constants.Company.company_name in data
            and data[constants.Company.company_name] != name
        ):
            await users_collection.update_many(
                {constants.Company.company: name},
                {"$set": {constants.Company.company: data[constants.Company.company_name]}},
            )
    except DuplicateKeyError as e:
        logger.error(f"Duplicate key error: {e}")
        raise CompanyAlredyExist()

# Function to update warehouse data
async def update_data_warehouse(name: str, data: dict):
    update_fields = {}
    for key, value in data.items():
        if key == "gates":
            continue
        update_fields[f"warehouses.$.{key}"] = value

    update_result = await companies_collection.update_one(
        {
            "company_name": name,
            "warehouses.warehouse_name": data["warehouse_name"],
        },
        {
            "$set": update_fields,  # Use update_fields directly
            "$addToSet": {
                "warehouses.$.gates": {"$each": data.get("gates", [])}
            },  # Use data for gates
        },
    )

    if not update_result:
        logger.error("Update warehouse data function error")
        raise WarehouseNotFound()
# ... (продолжение предыдущего кода)

# Function to add a new warehouse to a company
async def add_warehouse(company_name: str, data: dict):
    update_result = await companies_collection.update_one(
        {
            "company_name": company_name,
            constants.Company.deletionDate: {"$exists": False},
        },
        {"$addToSet": {"warehouses": data}},
    )
    if not update_result.matched_count:
        logger.error(f"Failed to add warehouse to company {company_name}: No matching records.")
        raise WarehouseNotFound()

    # if not update_result.modified_count:
    #     logging.error("add warehouse in company error modified count")
    #     raise AlreadyExistsException
async def delete_company_with_id(id ):
    await companies_collection.delete_one({"_id":ObjectId(id)})
# Function to mark a company as deleted by setting deletionDate
async def delete_company(company_name: str):
    query = {constants.Company.deletionDate: datetime.datetime.utcnow()}

    result = await companies_collection.update_one(
        {
            constants.Company.company_name: company_name,
            constants.Company.deletionDate: {"$exists": False},
        },
        {"$set": query},
    )

    if not result.matched_count:
        logging.error("delete_company: Company not found by company_name")
        raise DoesNotExist

# Function to temporarily place a product
async def temporarily_place(data: dict):
    await temporary_locations.insert_one(data)
    logger.info(f"Successfully placed product temporarily: {data}")

# Function to update the status of a product in temporary locations
async def update_temporary_status(_id, status):
    await temporary_locations.update_one(
        {constants.Locations.product_id: _id}, {"$set": {Products.status: status}}
    )
    logger.info(f"Updated temporary status for product ID {_id} to {status}.")

# Function to unload a product from temporary locations
async def unload_from_temporary(_id):
    await temporary_locations.delete_one({constants.Locations.product_id: _id})
    logger.info(f"Unloaded product ID {_id} from temporary locations.")

# Function to unload a product from its current location
async def unload_product(product_id: str):
    await locations_collection.update_one(
        {constants.Locations.product_id: product_id},
        {"$set": {constants.Locations.product_id: None}},
    )
    logger.info(f"Unloaded product ID {product_id} from its current location.")


# Function to change the status of a location
async def change_location_status(row: int, shelf: int, floor: int):
    filter_query = {"row": row, "shelf": shelf, "floor": floor}
    update_data = {"$set": {"status": "unsuitable"}}
    location_data = await locations_collection.update_one(filter_query, update_data)
    if location_data.modified_count > 0:
        logger.info(f"Successfully changed location status for row {row}, shelf {shelf}, floor {floor}.")
        return "success change"
    else:
        logger.warning(f"Failed to change location status for row {row}, shelf {shelf}, floor {floor}.")
        raise DoesNotExist

# Function to create a spoilage place for products
async def create_spoilage_place(spoilage_place: dict):
    await spoilages_collection.insert_one(spoilage_place)
    logger.info(f"Successfully created spoilage place: {spoilage_place}")

# Function to remove a product from spoilage place
async def remove_from_spoilage_place(product_id: str):
    await spoilages_collection.delete_one({Reports.product_id: product_id})
    logger.info(f"Successfully removed product ID {product_id} from spoilage place.")

# Function to create an unsuitable place for products
async def create_unsuitable_place(place_data: dict):
    await unsuitable_collection.insert_one(place_data)
    logger.info(f"Successfully created unsuitable place: {place_data}")

# Function to retrieve all data from the unsuitable place collection
async def get_all_data_from_collection():
    try:
        places = []
        all_data_cursor = unsuitable_collection.find({})
        all_data_list = await all_data_cursor.to_list(None)
        for place in all_data_list:
            place["_id"] = str(place.pop("_id"))
            places.append(place)
        logger.info(f"Successfully retrieved all data from unsuitable place collection.")
        return places
    except Exception as e:
        logger.error(f"Failed to retrieve all data from unsuitable place collection: {e}")
        raise e

# Function to retrieve an unsuitable place by ID
async def get_unsuitable_place_by_id(place_id: str) -> dict:
    object_id = ObjectId(place_id)
    place_data = await unsuitable_collection.find_one({"_id": object_id})
    if not place_data:
        logger.error(f"Unsuitable place not found by ID {place_id}.")
        raise DoesNotExist
    place_data["id"] = str(place_data.pop("_id"))
    logger.info(f"Successfully retrieved unsuitable place by ID {place_id}.")
    return place_data

