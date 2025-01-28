# import motor.motor_asyncio
# # import urllib.parse
# import asyncio
from ..database import db
from bson.objectid import ObjectId
# from fast_api.database import db

# Define the function as async
async def migrate_data_to_include_fields_with_defaults(target_collection:str, schema_changes:dict):

    try:
        collection = db[target_collection]
        # Query documents to update (those without new fields)
        documents_to_update = collection.find(
            {"$or": [{field: {"$exists": False}} for field in schema_changes.keys()]}
        )
        # Update documents with new fields and default values
        async for document in documents_to_update:
            update_data = {}
            for field, default_value in schema_changes.items():
                if field not in document:
                    update_data[field] = default_value
            if update_data:
                await collection.update_one({"_id": ObjectId(document["_id"])}, {"$set": update_data})
    except Exception as e:
        raise e

    # finally:
    #     # Close the MongoDB client connection
    #     client.close()

# # Example usage:
# if __name__ == "__main__":
#     # db_uri = "mongodb://root:Prometeo_2023@mongodb_container:27017"
#     target_collection = "users"
#     schema_changes = {
#         "new_field1": "default_value1",
#         "new_field2": "default_value2",
#     }
    
#     # Create an event loop and run the migration function
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(migrate_data_to_include_fields_with_defaults(target_collection, schema_changes))
#     loop.close()
