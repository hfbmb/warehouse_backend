# Installed packages
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware

# from prometheus_fastapi_instrumentator import Instrumentator
import time

# import psutil
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError


# Local packages
from .product.router import router as product_router
from .user.router import router as user_router
from .user.roles_router import role_router 
from .user.permission_router import permission_router
from .report.router import router as report_router
from .company.router import company_router
from .order.router import router as order_router
from .order.salesman_router import salesman_router
from .websocket.router import router as websocket_router
from .shipment_order.shipment_router import router as shipment_router
from .warehouse.router import warehouse_router 
from .warehouse.category_router import category_router
from .warehouse.zone_router import zone_router
from .warehouse.condition_router import condition_router
from . warehouse.rack_router import rack_router
from .warehouse.floor_router import floor_router
from .warehouse.cells_router import cell_router
from .warehouse.box_router import box_router
from .warehouse.type_box_router import type_router
from .constants import Errors
from .exceptions import BaseAPIException
from .config import (
    reports_example,
    products_example,
    product_example,
    companies_example,
)
import logging
from .database import setup_db,shudown_database

logging.basicConfig(
    # for example logging.getLogger("example_logger")  name ="example_logger"
    level=logging.DEBUG,  # Set the desired logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Display logs in the console
        # You can add other handlers here, like logging.FileHandler() to write logs to a file
    ],
)

app = FastAPI()
# Метрика использования системных ресурсов
# Использование процессора и памяти (CPU и Memory Usage)
# @app.get("/system-info")
# async def system_info():
#     cpu_percent = psutil.cpu_percent()
#     memory_info = psutil.virtual_memory()
#     return {"cpu_percent": cpu_percent, "memory_info": memory_info}

# @app.on_event("startup")
# async def startup_event():
#     Instrumentator().instrument(app).expose(app)

app.include_router(user_router)
app.include_router(company_router)
app.include_router(role_router)
app.include_router(permission_router)
app.include_router(warehouse_router)
app.include_router(category_router)
app.include_router(zone_router)
app.include_router(condition_router)
app.include_router(rack_router)
app.include_router(floor_router)
app.include_router(cell_router)
app.include_router(type_router)
app.include_router(box_router)
app.include_router(salesman_router)
app.include_router(order_router)
app.include_router(product_router)
app.include_router(report_router)
app.include_router(websocket_router)
app.include_router(shipment_router)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Adjust the frontend URL as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await setup_db()


@app.on_event("shutdown")
async def shutdown_event():
    # Close the database connection
    await shudown_database()

@app.exception_handler(BaseAPIException)
async def base_exception_handler(request: Request, exc: BaseAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={**exc.model().dict(), "timestamp": time.time()},
    )


@app.exception_handler(InvalidId)
async def invalid_id_exception_handler(request: Request, exc: InvalidId):
    return JSONResponse(
        status_code=400,
        content={"message": Errors.invalid_id, "timestamp": time.time()},
    )


@app.exception_handler(DuplicateKeyError)
async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
    return JSONResponse(
        status_code=208,
        content={"message": Errors.alr_exists, "timestamp": time.time()},
    )


app.openapi()["paths"]["/reports/{product_id}"]["get"]["responses"]["200"]["content"][
    "application/json"
]["example"] = reports_example
app.openapi()["paths"]["/products/"]["get"]["responses"]["200"]["content"][
    "application/json"
]["example"] = products_example
app.openapi()["paths"]["/products/{product_id}"]["get"]["responses"]["200"]["content"][
    "application/json"
]["example"] = product_example
app.openapi()["paths"]["/company/"]["get"]["responses"]["200"]["content"][
    "application/json"
]["example"] = companies_example


# Access the Swagger UI
@app.get("/docs", include_in_schema=False)
async def override_swagger_ui():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Custom Example")
