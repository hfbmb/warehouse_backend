# Import necessary modules and classes
from ..database import orders_collection  # Import the database collection
from .shpmemt_model import ShipmentOrder  # Import the ShipmentOrder model
from bson.objectid import ObjectId  # Import ObjectId for working with MongoDB IDs
from .exceptions import ShipmentEmpty, ShipmentId  # Import custom exceptions
import logging  # Import the logging module

# Define an asynchronous function to create a shipment order
async def create_shipment(order_data: dict):
    # Set the initial status of the order
    order_data["status"] = "Order added"
    # Insert the order data into the database collection
    await orders_collection.insert_one(order_data)
    # Return a success message
    return {"message": "Successfully created!!!"}

# Define an asynchronous function to retrieve all shipment orders based on a query
async def get_all_orders(query: dict):
    # Find orders in the database collection that match the given query
    orders = orders_collection.find(query)
    # Initialize an empty list to store the retrieved orders
    data = [] 
    # Iterate over the retrieved orders and convert MongoDB IDs to strings
    async for order in orders:
        order["id"] = str(order.pop("_id"))  # Convert MongoDB ID to string
        data.append(order)
    # If no orders are found, raise a custom exception
    if len(data) == 0:
        raise ShipmentEmpty
    # Return the retrieved orders
    return data

# Define an asynchronous function to retrieve a shipment order by its ID
async def get_shipment_order_by_id(order_id: str):
    # Find a shipment order in the database collection by its MongoDB ID
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    # If no order is found, raise a custom exception
    if not order:
        raise ShipmentId 
    # Convert the MongoDB ID to a string
    order["id"] = str(order.pop("_id"))
    # Return the retrieved shipment order
    return order

# Define an asynchronous function to delete a shipment order by a query
async def delete_shipment_order_by_id(query: dict):
    # Attempt to delete a shipment order based on the provided query
    res = await orders_collection.delete_one(query)
    # If no order is deleted, raise a custom exception
    if res.deleted_count <= 0:
        raise ShipmentId

# Define an asynchronous function to update a shipment order by its ID
async def update_shipment_order_by_id(order_id: str, order_data: dict):
    try:
        # Attempt to update a shipment order by its MongoDB ID
        result = await orders_collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": order_data}
        )
        # If no matching order is found, raise a custom exception
        if result.matched_count <= 0:
            raise ShipmentId
    except Exception as e:
        # Log any errors that occur during the update process
        logging.error("Update shipment error: %s", e)
        
        # Raise the original exception
        raise e
