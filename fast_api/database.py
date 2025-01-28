# Installed packages
import motor.motor_asyncio
import urllib.parse
from bson.objectid import ObjectId
# Local packages
from .user.constants import Users, Roles
from .company.constants import Locations, Company
from .product.constants import Products
from .order.constants import Orders
from .config import RACK_SIZE, FLOOR_LEVELS, SHELF_SIZE


# MongoDB connection
username = urllib.parse.quote_plus('root')
password = urllib.parse.quote_plus('Prometeo_2023')
# MONGO_DB = f'mongodb://10.138.0.14:27017,10.138.0.13:27017/replicaSet=mongoset'
MONGO_DB = f'mongodb://{username}:{password}@mongodb_container:27017'
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DB)
db = client['warehouse_db']


# Define the collections
products_collection = db["products"]
reports_collection = db["reports"]
users_collection = db["users"]
temporary_locations = db["temporary_locations"]
locations_collection = db["locations"]
companies_collection = db["companies"]
warehouses_collection = db["warehouse"]
orders_collection = db["orders"]
spoilages_collection = db["spoilages"]
unsuitable_collection = db["unsuitable_places"]
temporary_tokens_collection = db["tokens"]
categories_collection = db["categories"]
zones_collection = db["zones"]
conditions_collection = db["conditions"]
racks_collection = db["racks"]
floors_collection =db["floors"]
cells_collection = db["cells"]
boxes_collection = db["boxes"]
types_collection = db["types"]
roles_collection = db["roles"]
permissions_collection =db["permissions"]
# shipment_order_collection = db ["shipments"]
###Shutdown event database

async def shudown_database():
    await client.close()

async def setup_db():
    await users_collection.create_index(Users.email, unique=True)
    await users_collection.create_index(
        Users.deletionDate, expireAfterSeconds=10 * 86400
    )
    await temporary_locations.create_index(Locations.product_id, unique=True)
    await companies_collection.create_index(Company.company_name, unique=True)
    await companies_collection.create_index(
        Company.deletionDate, expireAfterSeconds=10 * 86400
    )
    await temporary_locations.create_index(Products.product_id, unique=True)
    await spoilages_collection.create_index(Products.product_id, unique=True)
    await temporary_tokens_collection.create_index("createdAt", expireAfterSeconds=600)
    await temporary_tokens_collection.create_index("token", unique=True)
    await orders_collection.create_index(
        Orders.deletionDate, expireAfterSeconds=10 * 86400
    )
    await products_collection.create_index(
        Products.deletionDate, expireAfterSeconds=10 * 86400
    )
    #  default users
    director = {
        Users.firstname: Roles.director,
        Users.lastname: Roles.director,
        Users.hashed_password: "$2y$10$.aETYloFED80hny1O3.nYOTGsRRNL0RDxLCS.h7pBnFFRDe2LVkWK",
        Users.role: Roles.director,
        Users.email: "director@mail.ru",
        Users.telephone: "+7 (708) 153-45-23",
        Users.company: "company1",
        Users.user_address:{
            Users.zip_code:"zip_code",
            Users.street:"street",
            Users.city:"Astana",
            Users.country:"Qazaqstan",
            Users.region:"Aqmola"
        },
        Users.is_confirmed :True
    }
    salesman = {
        Users.firstname: Roles.salesman,
        Users.lastname: Roles.salesman,
        Users.hashed_password: "$2y$10$a77IpwlA3/41uCcrDL59re9q2WDLP.LtpZxBNDztpZU.HB0/7ibfm",
        Users.role: Roles.salesman,
        Users.email: "salesman@mail.ru",
        Users.telephone: "+7 (708) 153-45-12",
        Users.company: "company1",
        Users.user_address:{
            Users.zip_code:"zip_code",
            Users.street:"street",
            Users.city:"Astana",
            Users.country:"Qazaqstan",
            Users.region:"Aqmola"
        },
        Users.is_confirmed :True

    }
    manager = {
        Users.firstname: Roles.manager,
        Users.lastname: Roles.manager,
        Users.hashed_password: "$2y$10$RZDJznxcAeGLypUrguh/2O95dSCY5hqUQar5U.XEfrsJR.oPVYMXm",
        Users.role: Roles.manager,
        Users.email: "manager@mail.ru",
        Users.telephone: "+7 (708) 153-45-45",
        Users.company: "company1",
        Users.warehouse: "warehouse1",
        Users.user_address:{
            Users.zip_code:"zip_code",
            Users.street:"street",
            Users.city:"Astana",
            Users.country:"Qazaqstan",
            Users.region:"Aqmola"
        },
        Users.is_confirmed :True
    }
    dispatcher = {
        Users.firstname: Roles.dispatcher,
        Users.lastname: Roles.dispatcher,
        Users.hashed_password: "$2y$10$LSNuQlVEbsztXc0jPRLrPOXWV.0.rlRXGd26NjbRKQQAilXKIFel2",
        Users.role: Roles.dispatcher,
        Users.email: "dispatcher@mail.ru",
        Users.telephone: "+7 (708) 153-45-78",
        Users.company: "company1",
        Users.warehouse: "warehouse1",
        Users.user_address:{
            Users.zip_code:"zip_code",
            Users.street:"street",
            Users.city:"Astana",
            Users.country:"Qazaqstan",
            Users.region:"Aqmola"
        },
        Users.is_confirmed :True
    }
    controller = {
        Users.firstname: Roles.controller,
        Users.lastname: Roles.controller,
        Users.hashed_password: "$2y$10$MXdBiT9ye.xs49y6cn/QAeWaBFGJ0URy/ZHFT9Ff8iXAc9rBbWsWW",
        Users.role: Roles.controller,
        Users.email: "controller@mail.ru",
        Users.telephone: "+7 (708) 153-45-59",
        Users.company: "company1",
        Users.warehouse: "warehouse1",
        Users.user_address:{
            Users.zip_code:"zip_code",
            Users.street:"street",
            Users.city:"Astana",
            Users.country:"Qazaqstan",
            Users.region:"Aqmola"
        },
        Users.is_confirmed :True
    }
    warehouseman = {
        Users.firstname: Roles.warehouseman,
        Users.lastname: Roles.warehouseman,
        Users.hashed_password: "$2y$10$cXjwaEbWj5D7UEnyxHc6J.rfzwsuFf5L43HvZuG4NUdgbiuzx0wvK",
        Users.role: Roles.warehouseman,
        Users.email: "warehouseman@mail.ru",
        Users.telephone: "+7 (708) 153-45-65",
        Users.company: "company1",
        Users.warehouse: "warehouse1",
        Users.user_address:{
            Users.zip_code:"zip_code",
            Users.street:"street",
            Users.city:"Astana",
            Users.country:"Qazaqstan",
            Users.region:"Aqmola"
        },
        Users.is_confirmed :True
    }
    loader = {
        Users.firstname: Roles.loader,
        Users.lastname: Roles.loader,
        Users.hashed_password: "$2y$10$5zBqpJPEJbnqB6OZ2p0C/e3.lutmVyXD/XTSTl/BeAtSUMGh9s/62",
        Users.role: Roles.loader,
        Users.email: "loader@mail.ru",
        Users.telephone: "+7 (708) 153-45-57",
        Users.company: "company1",
        Users.warehouse: "warehouse1",
        Users.user_address:{
            Users.zip_code:"zip_code",
            Users.street:"street",
            Users.city:"Astana",
            Users.country:"Qazaqstan",
            Users.region:"Aqmola"
        },
        Users.is_confirmed :True
    }
    employee = {
        Users.firstname: Roles.employee,
        Users.lastname: Roles.employee,
        Users.hashed_password: "$2y$10$r0HkAWSojnCNSamnL86Mheh9kia8gy6prvmj72imv7.DVYXrWzwBi",
        Users.role: Roles.employee,
        Users.email: "employee@mail.ru",
        Users.telephone: "+7 (708) 153-45-25",
        Users.company: "company1",
        Users.warehouse: "warehouse1",
        Users.user_address:{
            Users.zip_code:"zip_code",
            Users.street:"street",
            Users.city:"Astana",
            Users.country:"Qazaqstan",
            Users.region:"Aqmola"
        },
        Users.is_confirmed :True
    }
    client = {
        Users.firstname: Roles.client,
        Users.lastname: Roles.client,
        Users.hashed_password: "$2y$10$E/oOtckcsB6EUxB.JI79v.7xAViDUONiRn2WL4DxZnHZ7xuev1Vha",
        Users.role: Roles.client,
        Users.email: "client@mail.ru",
        Users.telephone: "+7 (708) 153-45-33",
        Users.company: "company1",
        Users.warehouse: "warehouse1",
        Users.user_address:{
            Users.zip_code:"zip_code",
            Users.street:"street",
            Users.city:"Astana",
            Users.country:"Qazaqstan",
            Users.region:"Aqmola"
        },
        Users.is_confirmed :True
    }
    users_collection.insert_many(
        [
            director,
            salesman,
            manager,
            controller,
            dispatcher,
            warehouseman,
            loader,
            employee,
            client,
        ]
    )
    #Default permissions 
    ADDITIONAL_PERMISSIONS = [
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
    {"permission_name":"delete_main_order"},
    # {"permission_name": "start_work_on_order"},
    {"permission_name": "view_all_orders"},
    # {"permission_name": "view_order_details"},
    {"permission_name":"create_sub_order"},
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
    # {"permission_name":""},
    # {"permission_name":""},
    # {"permission_name":""},    
    # Add any other specific permissions you might require
    ]
    permissions_collection.insert_many(ADDITIONAL_PERMISSIONS)

    

async def migrate_data_to_include_fields_with_defaults(target_collection:str, schema_changes:dict):
    try:
        collection = db[target_collection]
        documents_to_update = collection.find(
            {"$or": [{field: {"$exists": False}} for field in schema_changes.keys()]}
        )
        for document in documents_to_update:
            update_data = {}
            for field, default_value in schema_changes.items():
                if field not in document:
                    update_data[field] = default_value
            if update_data:
                collection.update_one({"_id": ObjectId(document["_id"])}, {"$set": update_data})
    finally:
        client.close()