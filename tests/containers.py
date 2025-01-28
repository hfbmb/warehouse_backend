# containers.py

from testcontainers.mongodb import MongoDbContainer

def get_mongo_container():
    mongo_container = MongoDbContainer("mongo:4.4")
    container = mongo_container.start()
    return container, mongo_container.get_connection_url()
