# Installed packages
from bson.objectid import ObjectId
import logging

# Local packages
from .report.models import Invoice
from .product.constants import Products
from .order.constants import Orders
from .company.constants import Locations, Company
from .exceptions import DoesNotExist, NotFoundError
from .database import (
    products_collection,
    companies_collection,
    locations_collection,
    reports_collection,
)
from .user.constants import Roles


async def update_status(product_id: str, status: str):
    await products_collection.update_one(
        {Products.id: ObjectId(product_id)}, {"$set": {Products.status: status}}
    )


# async def allocate_product_warehouse(product_id: str, row: int, floor: int, shelf: int):
#     await products_collection.update_one({Products.id: ObjectId(product_id)},
#                                          {"$set": {Products.warehouse_row: row,
#                                                    Products.floor_level: floor,
#                                                    Products.shelf: shelf}})


async def get_id_by_coords(row: int, floor: int, shelf: int):
    doc = await locations_collection.find_one(
        {Locations.name: f"{row}:{floor}:{shelf}"}, {Locations.id: 1}
    )
    return doc[Locations.id]


async def allocate_product_warehouse(product_id: str, row: int, floor: int, shelf: int):
    location_id = await get_id_by_coords(
        row, floor, shelf
    )  # id of a location by coordinates
    await products_collection.update_one(
        {Products.id: ObjectId(product_id)},
        {"$set": {Products.location_id: location_id}},
    )
    await locations_collection.update_one(
        {Locations.id: location_id}, {"$set": {Locations.product_id: product_id}}
    )


async def create_invoice(report: Invoice):
    await reports_collection.insert_one(report)


async def check_company_warehouse(order: dict, role: str) -> None:
    query = {
        Company.company_name: order[Orders.recipient],
        Company.deletionDate: {"$exists": False},
    }
    if Roles.admin != role:
        query[Company.warehouses] = {
            "$elemMatch": {Company.company_name: order[Orders.warehouse]}
        }
    result = await companies_collection.find_one(query)

    if not result:
        raise DoesNotExist


async def delete_product(sku: str, quantity: int):
    product_data = await products_collection.find_one({"sku": sku})
    if not product_data:
        return NotFoundError
    else:
        new_quantity = product_data["quantity"] - quantity
        update_result = await products_collection.update_one(
            {"sku": sku}, {"$set": {"quantity": new_quantity}}
        )
        try:
            update_result.modified_count > 0
            logging.info("updated quantity very well")
            return "ok"
        except Exception as e:
            logging.error("delete product err: ", str(e))
            return "error!"
