# from decouple import config
# import os
import os.path as path
from starlette.config import Config

dotenv_path = path.abspath(path.join(__file__ ,"../../../.env"))
config = Config(dotenv_path)
SMTP_PORT = int(config('SMTP_PORT', default=587))
MAIL_USERNAME = config('MAIL_USERNAME',default="noreply@prometeochain.io")
MAIL_PASSWORD = config('MAIL_PASSWORD',default="Prometeo-2023!!")
MAIL_SERVER = config('MAIL_SERVER',default="smtp.hostinger.com")


RACK_SIZE = 20
FLOOR_LEVELS = 1
SHELF_SIZE = 20
IMAGE_DIRECTORY = "images"
DOCUMENTS_DIRECTORY = "documents"
MAX_IMAGE_UPLOAD_SIZE = 10 * 1024 * 1024  # threshold 10 MB for uploading single file
MAX_DOCUMENT_UPLOAD_SIZE = 100 * 1024 * 1024
DB_USER = "root"
DB_PASSWORD = "Prometeo_2023"
DB_HOST = "mongodb_container"
DB_PORT = 27017
DB_NAME = "warehouse_db"
DB_NAME_TEST = "warehouse_db_test"
ALLOWED_MEDIA_TYPES = [
    "image/apng",
    "image/avif",
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
    "application/msword"
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]
URL_PARTS = {
    "DOMAIN_NAME": "warehouse.prometeochain.io",
    "HTTP": "http",
    "HTTPS": "https",
    "ENDPOINT": "orders/create",
    "TOKEN": "token",
    "COMPANY": "company",
    "WAREHOUSE": "warehouse",
    "ORDER_ID": "order_id",
}
reports_example = [
    {
        "id": "df5tgyhuj...",
        "date_of_arrival": 2906.2023,
        "product_id": "d45fr6ty7u...",
        "timestamp": 123589625632.78965412321,
    },
    {
        "id": "4ed5f6g7hu...",
        "quality_check_passed": True,
        "product_id": "e5r6t7y8uh...",
        "timestamp": 123589625632.78965412321,
    },
    {
        "id": "d45f6g7yhuj...",
        "warehouse_row": 1,
        "shelf_num": 1,
        "floor_level": 1,
        "product_id": "rt67yu6rt7...",
        "timestamp": 123589625632.78965412321,
    },
]

products_example = [
    {
        "id": "d4f5g6h7j8k9l...",
        "name": "product0",
        "quantity": 859,
        "weight": 1252.385,
        "height": 168,
        "width": 42,
        "length": 563,
        "booking_date": 2906.2023,
        "due_arrival_date": 2806.2023,
        "packing_type": "pallets",
    },
    {
        "_id": "649a873...",
        "name": "product1",
        "quantity": 452,
        "weight": 485.64152,
        "height": 251,
        "width": 365,
        "length": 120,
        "booking_date": 1687884752.3856294,
        "due_arrival_date": 270620.23,
        "packing_type": "pallets",
        "date_of_arrival": 462461,
        "quality_check_passed": True,
        "location_id": "649928b3...",
    },
    {
        "id": "d45f6gh7...",
        "name": "product2",
        "quantity": 325,
        "weight": 154,
        "height": 236,
        "width": 4852,
        "length": 415,
        "booking_date": 48520.85285,
        "due_arrival_date": 45030.38526,
        "packing_type": "pallets",
        "schedule": 152852.54852,
        "place": 45,
        "time": 48523.44565263,
        "warehouse_team": ["derftgyhu...", "edrcftgyh...", "d45f6g7h..."],
        "responsible_worker": "d4f5g67h8...",
        "date_of_arrival": 45030.38526,
        "quality_check_passed": True,
        "location_id": "d4f5g6h7j...",
        "frequency_of_use": 2,
    },
]

product_example = {
    "id": "d45f6gh7...",
    "name": "product2",
    "quantity": 325,
    "weight": 154,
    "height": 236,
    "width": 4852,
    "length": 415,
    "booking_date": 48520.85285,
    "due_arrival_date": 45030.38526,
    "packing_type": "pallets",
    "schedule": 152852.54852,
    "place": 45,
    "time": 48523.44565263,
    "warehouse_team": ["derftgyhu...", "edrcftgyh...", "d45f6g7h..."],
    "responsible_worker": "d4f5g67h8...",
    "date_of_arrival": 45030.38526,
    "quality_check_passed": True,
    "location_id": "d4f5g6h7j...",
    "frequency_of_use": 2,
}

companies_example = [
    {
        "logo": "path/path/logo.jpeg",
        "name": "company1",
        "bin": "45d1dxs...",
        "website": "www.vrfvrtferv.com/fgrgrtgvrtgfer/",
        "email": "com1@email.com",
        "fax": "748554f5",
        "phone": {"$numberLong": "87457185411"},
        "zip_code": "592fr59",
        "hq_address": "fdvtvrfe vfre58",
        "street": "frefe",
        "city": "vfddvt",
        "region": "vgrtfv",
        "country": "frfvcfdcv",
        "stamp": "path/path/stamp.pdf",
    },
    {
        "logo": "path/path/logo.jpeg",
        "name": "company2",
        "bin": "45d1dxs4s51s54",
        "website": "www.vrfvrtferv.com/fgrgrtgvrtgfer/",
        "email": "com1@email.com",
        "fax": "748554f5",
        "phone": {"$numberLong": "87457185411"},
        "zip_code": "592fr59",
        "hq_address": "fdvtvrfe vfre58",
        "street": "frefe",
        "city": "vfddvt",
        "region": "vgrtfv",
        "country": "frfvcfdcv",
        "stamp": "path/path/stamp.pdf",
    },
    {
        "logo": "path/path/logo.jpeg",
        "name": "company3",
        "bin": "45d1dxs4s51s54",
        "website": "www.vrfvrtferv.com/fgrgrtgvrtgfer/",
        "email": "com1@email.com",
        "fax": "748554f5",
        "phone": {"$numberLong": "87457185411"},
        "zip_code": "592fr59",
        "hq_address": "fdvtvrfe vfre58",
        "street": "frefe",
        "city": "vfddvt",
        "region": "vgrtfv",
        "country": "frfvcfdcv",
        "stamp": "path/path/stamp.pdf",
    },
]
