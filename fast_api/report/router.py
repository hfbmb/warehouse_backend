# Installed packages
from fastapi import APIRouter, File, Depends, UploadFile, HTTPException
from typing import Annotated
from fastapi.params import Path
import time, logging
from typing import Optional
from bson import ObjectId
from datetime import datetime,timedelta


# Local packages
from ..warehouse.service import get_product_warehouse_category
from ..user.service import get_user_by
from ..websocket.router import manager
from ..dependencies import (
    get_exception_responses,
    get_current_user,
    check_role_access,
    check_data,
    upload_files,
    generate_sku,
    is_quality_checked,
    upload_files_for_place,
)
from ..user.models import DBUser
from ..user.constants import Roles, Users
from ..user.service import check_user_status_for_order
from ..product.constants import Messages as ProdMessages, Products
from ..product.service import (
    get_product_by_id_,
    update_product,
    verification,
    # confirmed_location,
    create_product,
    update_many_products,
)
from ..company.service import (
    temporarily_place,
    update_temporary_status,
    # unload_product_in_cell,
    unload_from_temporary,
    create_spoilage_place,
    unload_product,
    remove_from_spoilage_place,
    get_unsuitable_place_by_id,
    get_all_data_from_collection,
    create_unsuitable_place,
    change_location_status,
    check_order_company_and_or_warehouse,
    # get_product_warehouse_category,
    get_company
)
from ..company.constants import Locations, Company, Warehouses
from ..order.email_sender import send_email_to_client,scheduler,IntervalTrigger
from ..order.service import (
    update_order_product_status,
    find_product_by_name,
    get_order_by_id,
    update_order_status,
    check_order_status,
    update_order,
    check_order_product_status
)
from .models import (
    ProductArrival,
    QualityCheck,
    ProductReturn,
    ProductUnload,
    InvoiceUnsuitablePlace,
    UnsuitablePlace,
    DispatcherModel,
    PackagingQualityCheck,
)
from . import service
from . import constants
# from ..warehouse import Warehouse as CusWarehouse
from ..config import IMAGE_DIRECTORY, MAX_IMAGE_UPLOAD_SIZE
from ..exceptions import (
    UnauthorizedException,
    PermissionException,
    DoesNotExist,
    AlreadyCheckedException,
    BaseAPIException,
    Success,
    ConflictException,
    AlreadyExistsException,
    EmptyFileUploadException,
    RequestEntityTooLargeException,
    UnsupportedMediaTypeException,
    QualityCheckFailed,
    InvalidIdException,
    NotFoundException,
    DuplicateKeyException,
)
from ..constants import Messages
from ..company.models import CompanyUpdateInfo

router = APIRouter(prefix="/reports", tags=["reports"])

# wh = CusWarehouse()


@router.get(
    "/{product_id}",
    response_model=list,
    responses=get_exception_responses(UnauthorizedException, PermissionException),
)
async def get_all_reports(
    product_id: str, current_user: DBUser = Depends(get_current_user)
):
    try:
        check_role_access(
            current_user.role,
            [Roles.admin, Roles.director, Roles.manager, Roles.controller],
        )
        if current_user.role == Roles.controller:
            pass
        reports = await service.get_reports(product_id)
    except BaseAPIException as e:
        raise e

    return reports


# api для диспетчера он проверит, если все норм создается отчет
# если нет то он description жазады и status фейлед
@router.put(
    "/{order_id}/check_documents",
    response_model=dict,
    responses=get_exception_responses(
        UnauthorizedException, PermissionException, DoesNotExist
    ),
)
async def check_documents_dispatcher(
    order_id: str,
    check_data: DispatcherModel,
    current_user: DBUser = Depends(get_current_user),
):
    # code started
    roles = [Roles.manager, Roles.dispatcher]
    check_role_access(current_user.role, roles)
    await check_order_company_and_or_warehouse(
        {
            Company.company_name: current_user.company,
            Company.warehouses
            + "."
            + Warehouses.warehouse_name: current_user.warehouse,
        }
    )
    await check_user_status_for_order(current_user.id, order_id)
    if check_data.order_accepted == "false":
        status = "failed"
    else:
        status = "successful"
    data = {}
    for key, value in check_data.dict().items():
        if value is not None and value != "string" and value != "":
            data[key] = value
    # order_data нам нужен для сравнения данных
    # например для plomb, and date time t.c.c
    # order_data =await get_order_by_id(order_id)
    # print(order_data)
    data["order_id"] = order_id
    data["user_id"] = current_user.id
    data["status"] = status
    await service.create_every_employee_report(data)
    await update_order_status(order_id, "all_documents_verifed")
    order_data = await get_order_by_id(order_id=order_id)
    user_data = await get_user_by("email",order_data["e_mail"])
    message = {"current_user":current_user.role,
               "order_status":status,
               "order_id":order_id,
               "description":check_data.accepted_description}
    await manager.send_message(user_id=user_data.id,message=str(message))
    return {"message": "succesfully created dispatcher report"}


# Проверка упаковки продукта, контроллер
@router.put(
    "/{order_id}/packaging_check",
    responses=get_exception_responses(
        UnauthorizedException,
        PermissionException,
        DoesNotExist,
        AlreadyCheckedException,
    ),
)
async def packaging_check_controller(
    order_id: str,
    packing_data: PackagingQualityCheck = Depends(PackagingQualityCheck),
    current_user: DBUser = Depends(get_current_user),
    file: UploadFile = File(None),
):
    roles = [Roles.manager, Roles.controller]
    check_role_access(current_user.role, roles)
    await check_order_company_and_or_warehouse(
        {
            Company.company_name: current_user.company,
            Company.warehouses
            + "."
            + Warehouses.warehouse_name: current_user.warehouse,
        }
    )
    await check_user_status_for_order(current_user.id, order_id)
    await check_order_status(order_id, "all_documents_verifed")
    data = {}
    for key, value in packing_data.dict().items():
        if value is not None and value != "string" and value != "":
            data[key] = value
    if file:
        files = []
        files.append(file)
        file_paths = upload_files_for_place(files, "packing",MAX_IMAGE_UPLOAD_SIZE)
        data["images"] = file_paths
    data["order_id"] = order_id
    data["user_id"] = current_user.id
    data["user_name"] = current_user.firstname
    data["user_role"] = current_user.role
    data["status"] = "succes_packing"
    data["verification_stage"] = "packing"
    await update_order_product_status(
        order_id, packing_data.product_name, "succes_packing"
    )
    await service.create_every_employee_report(data)
    return {"message": "succesfully created controller report"}


# For arrival date  warehouseman
# Qr код наклейвает на товар
@router.post(
    "/arrival_date",
    response_model=dict,
    responses=get_exception_responses(
        UnauthorizedException,
        PermissionException,
        DoesNotExist,
        AlreadyCheckedException,
    ),
)
async def product_arrival_insert(
    product_data: ProductArrival, current_user: DBUser = Depends(get_current_user)
):
    check_role_access(
        current_user.role,
        [
            Roles.admin,
            Roles.director,
            Roles.manager,
            Roles.controller,
            Roles.dispatcher,
            Roles.warehouseman,
        ],
    )
    product_data = product_data.dict()
    order_data = await get_order_by_id(product_data[Products.order_id])
    product_dataa = await find_product_by_name(
        product_data[Products.order_id], product_data[Products.product_name]
    )
    product_dataa["client_email"]=order_data["e_mail"]
    if product_dataa["status"] != "succes_packing":
        raise HTTPException(
            status_code=404,
            detail="Cannot start this product, because it has not been successfully packed.",
        )
    return_message = ""
    quantity_of = 0
    if product_dataa[Products.quantity] - product_data[Products.quantity] != 0:
        # status_report="failed"
        quantity_of = product_dataa[Products.quantity] - product_data[Products.quantity]
        if quantity_of > 0:
            return_message = f"missing in the order of {quantity_of} pieces of goods"
        else:
            return_message = f"exceeded on the order of {quantity_of} pieces of goods"
    else:
        return_message = "all goods are"
        # status_report="succes"
    product_dataa[Products.id_] = ObjectId(product_data["product_id"])
    product_dataa[Products.status] = ProdMessages.status_arrival
    product_dataa[Products.date_of_arrival] = time.time()
    product_dataa[Products.order_id] = product_data[Products.order_id]
    product_dataa[Products.warehouse_team].pop()
    product_dataa[Products.quantity] = product_data[Products.quantity]
    product_dataa["how_much_is_missing"] = quantity_of
    report_info = {
        Products.date_of_arrival: product_dataa[Products.date_of_arrival],
        Products.product_id: product_data["product_id"],
        Products.timestamp: time.time(),
        Users.user_id: current_user.id,
        Users.firstname: current_user.firstname,
        "description": return_message,
        Products.status: ProdMessages.status_arrival,
    }
    temporary_place = {
        Users.user_id: current_user.id,
        Products.name: product_data[Products.temporary_location],
        Products.product_id: product_data["product_id"],
        Products.status: "not yet",
        Products.timestamp: time.time(),
    }
    await create_product(product_dataa)
    await update_order_product_status(
        product_data["order_id"],
        product_dataa[Products.product_name], ProdMessages.status_arrival,
    )
    await service.create_report(report_info, Products.date_of_arrival)
    await temporarily_place(temporary_place)

    return {
        constants.Messages.message: ProdMessages.status_arrival
        + " and "
        + return_message
    }


# Проверка качества товара контроллер
@router.put(
    "/{product_id}/check_quality",
    response_model=dict,
    responses=get_exception_responses(
        UnauthorizedException,
        PermissionException,
        NotFoundException,
        ConflictException,
        AlreadyCheckedException,
        AlreadyExistsException,
        EmptyFileUploadException,
        RequestEntityTooLargeException,
        UnsupportedMediaTypeException,
    ),
)
async def check_quality(
    files: Annotated[list[UploadFile], File(...)],
    report: QualityCheck = Depends(QualityCheck),
    current_user: DBUser = Depends(get_current_user),
    product_id: str = Path(...),
):
    check_role_access(current_user.role, [Roles.controller])
    report_dict = report.dict()
    product = await get_product_by_id_(product_id)
    # order_data = await get_order_by_id(product["order_id"])
    check_data(product)
    # encoded_files = encode_files(files)
    file_paths = upload_files(files, product_id, MAX_IMAGE_UPLOAD_SIZE, IMAGE_DIRECTORY)

    product_info = {
        Users.user_id: current_user.id,
        Products.quality_check_passed: report_dict[Products.quality_check_passed],
        Products.product_id: product_id,
        Products.timestamp: time.time(),
        # Products.product_images: encoded_files
        Products.product_images: file_paths,
    }

    await service.create_report(product_info, Products.quality_check_passed)
    await verification(product_id, report_dict[Products.quality_check_passed])

    data = {
        Products.product_images: file_paths,
        Users.user_id: current_user.id,
        Products.quality_check_passed: report_dict[Products.quality_check_passed],
    }
    if report_dict[Products.quality_check_passed]:
        sku = generate_sku(product)
        data[Products.status] = ProdMessages.status_approved
        data[Products.sku] = sku
        await update_temporary_status(product_id, "about to be allocated")
        status = ProdMessages.status_approved
    else:
        spoilage_place = {
            Products.name: report_dict[Products.spoilage_place],
            Products.product_id: product_id,
            Products.comment: report_dict[Products.comment],
            Products.timestamp: time.time(),
        }
        await unload_from_temporary(product_id)
        await create_spoilage_place(spoilage_place)
        data[Products.status] = ProdMessages.status_disapproved
        status = ProdMessages.status_disapproved
    await update_order_product_status(
        product[Products.order_id], product[Products.product_name], status
    )
    await update_product(product_id, data)
    return {ProdMessages.message: Messages.qlty_ch_compl}


# Размещение на складе
@router.put(
    "/{product_id}/allocate_warehouse",
    response_model=Success,
    responses=get_exception_responses(
        UnauthorizedException,
        PermissionException,
        DoesNotExist,
        QualityCheckFailed,
        AlreadyExistsException,
    ),
)
async def allocate_warehouse(
    product_id, current_user: DBUser = Depends(get_current_user)
):
    check_role_access(current_user.role, [Roles.warehouseman])
    #         product = await get_product_by_id(product_id, current_user.company)
    product = await get_product_by_id_(product_id)
    is_quality_checked(product)
    product[Products.status]=ProdMessages.status_allocated
    query ={"company_name":current_user.company,"warehouse_name":current_user.warehouse}
    product_data = await get_product_warehouse_category(
                query=query, product_data=product
            )
    product_data.pop("_id")
    report = {
        Users.user_id: current_user.id,
        Locations.cell_number: product_data["cell_number"],
        Locations.rack_number: product_data["rack_number"],
        Locations.floor_number: product_data["floor_number"],
        Products.product_id: product_id,
        Products.timestamp: time.time(),
    }
    product_data[Users.user_id]=current_user.id
    await update_product(
        product_id,
        product_data
    )
    await service.create_report(report, Locations.cell_number)
    return {Messages.message: constants.Messages.pr_aloc_in_wh}


@router.put(
    "/{product_id}/confirm_location",
    response_model=Success,
    responses=get_exception_responses(
        UnauthorizedException,
        PermissionException,
        AlreadyExistsException,
        InvalidIdException,
        DoesNotExist,
    ),
)
async def confirm_location(
    product_id, confirmed: bool, current_user: DBUser = Depends(get_current_user)
):
    check_role_access(current_user.role, [Roles.loader])
    product = await get_product_by_id_(product_id)
    is_quality_checked(product)
    confirmation_report = {
        Users.user_id: current_user.id,
        Products.location_confirmed: confirmed,
        Locations.product_id: product_id,
        Products.timestamp: time.time(),
    }

    data = {
        Users.user_id: current_user.id,
        Products.location_confirmed: confirmed,
        Products.status: ProdMessages.status_confirmed,
    }
    # product =await get_product_by_id_(product_id)
    # await service.create_report(confirmation_report, Products.location_confirmed)
    await update_product(product_id,data)
    # await confirmed_location(product_id, data)
    await unload_from_temporary(product_id)

    return {Messages.message: constants.Messages.pr_verf_scs}


@router.put(
    "/{product_id}/unallocate_product",
    response_model=Success,
    responses=get_exception_responses(
        UnauthorizedException,
        PermissionException,
        InvalidIdException,
        DoesNotExist,
        DuplicateKeyException,
    ),
)
async def unallocate_product(
    product_id:str, 
    shipment_order_id : str,
    report: ProductUnload,
      current_user: DBUser = Depends(get_current_user)
):
    check_role_access(current_user.role, [Roles.loader])
    #         product = await get_product_by_id(product_id, current_user.company)
    product = await get_product_by_id_(product_id)
    unload_report = report.dict()
    unload_report["product_id"]=product_id
    unload_report[Products.id] = product_id
    unload_report[Products.timestamp] = time.time()
    unload_report[Users.user_id] = current_user.id
    temporary_place = {
        Products.name: unload_report[Products.temporary_location],
        Products.product_id: product_id,
        Products.status: "to pack",
        Products.timestamp: time.time(),
    }
    product["quantity_un"]= unload_report["quantity"]
    await unload_product_in_cell(current_user.company,
                                 current_user.warehouse,
                                 product_data=product)
    await temporarily_place(temporary_place)
    await service.create_report(unload_report, Products.is_unloaded)
    product["quantity"]=product["quantity"]-unload_report["quantity"]
    status = str
    if product["quantity"]==0:
        status= ProdMessages.status_unallocated
    else:
        status=product["status"]
    await update_product(
        product_id,
        {
            "quantity":product["quantity"],
            Products.status: status,
            Users.user_id: current_user.id,
        },
    )
    await update_order_product_status(order_id=shipment_order_id,
                                      product_name=product["product_name"],
                                      status="ready_to_customer")

    return {Messages.message: constants.Messages.pr_unl_scs}


@router.put(
    "/{product_id}/return_suppliers",
    response_model=Success,
    responses=get_exception_responses(
        UnauthorizedException,
        PermissionException,
        InvalidIdException,
        AlreadyExistsException,
        DoesNotExist,
    ),
)
async def return_suppliers(
    product_id: str,
    report: ProductReturn,
    current_user: DBUser = Depends(get_current_user),
):
    check_role_access(current_user.role, [Roles.director, Roles.admin, Roles.manager])

    return_report = report.dict()
    return_report[Locations.product_id] = product_id
    return_report[Products.timestamp] = time.time()
    return_report[Users.user_id] = current_user.id

    await verification(product_id, False)
    await service.create_report(return_report, Products.quality_complaints)
    await update_product(
        product_id,
        {Products.status: ProdMessages.status_returnal, Users.user_id: current_user.id},
    )
    await remove_from_spoilage_place(product_id)

    return {Messages.message: constants.Messages.pr_rtrnd_to_splrs}


@router.put(
    "/{order_id}/send_to_customer",
    response_model=Success,
    responses=get_exception_responses(
        UnauthorizedException,
        PermissionException,
        DuplicateKeyException,
        QualityCheckFailed,
    ),
)
async def send_to_customer(
    order_id:str, 
    current_user: DBUser = Depends(get_current_user)
):
    check_role_access(
        current_user.role, [Roles.manager, Roles.controller, Roles.warehouseman]
    )
    company_data = await get_company(current_user.company)
    order_data = await get_order_by_id(order_id=order_id)
    ok =await check_order_product_status(order_data["products"],status="ready_to_customer")
    if ok:
        pass
    # report ={}
    # report["order_data"] = order_data
    # report[Products.timestamp] = time.time()
    # report[Users.user_id] = current_user.id
    # # is_quality_checked(product)
    # await service.create_report(report, Products.destination)
    data_for_websocket ={
        "order_id":order_id,
        "description":f"We are pleased to inform you that your order number {order_id} is ready for pickup.",
        "Today":"you can pick up your order from 8:00 am to 6:00 pm and in case of lateness a penalty will be charged."
    }
    await manager.send_message(user_id=order_data["client_id"],
                               message=str(data_for_websocket))
    # Prepare an email description for the client.
    description = f"""
        <html>
        <head>
            <style>
                /* Добавьте стили CSS по вашему усмотрению */
            </style>
        </head>
        <body>
            <p>Dear Valued Client,</p>
            <p>Thank you for your order</p>
            <ul>
                <li>Website: <a href="http://warehouse.prometeochain.io/">http://warehouse.prometeochain.io/</a></li>
            </ul>
            <p>We are pleased to inform you that your order number {order_id} is ready for pickup.</p>
            <p>you can pick up your order from 8:00 am to 6:00 pm and in case of lateness a penalty will be charged.</p>
            <p>If this time is convenient for you, please confirm and we will ensure your order is ready to be received</p>
            <p>If you have any other questions, please contact us at <a href="mailto:noreply@prometeochain.io">noreply@prometeochain.io</a>. We're here to help!</p>
            <p>Thank you for choosing us. Have a great day!</p>
        </body>
        </html>
        """
    # Prepare email data and send an order confirmation email to the client.
    email_data ={
        "office_email":company_data["office_email"],
        # "office_password":company_data["office_password"],
        "order_id":order_id,
        "recipient_email":order_data["client_email"],
        "description" : description,
        "subject":"Your order is ready",
    }
    await send_email_to_client(email_data=email_data)
    # Получите текущее время
    current_time = datetime.now()
    last_notification_time = current_time + timedelta(days=1)
    if current_time.weekday() ==6:
        last_notification_time +=timedelta(days=1)
    # Определите интервал, который нужно добавить к текущему времени (например, 5 минут)
    order_data["start_notification_time"]=current_time
    order_data["last_notification_time"]=last_notification_time
    order_data["status"]="waiting_for_customer"
    await update_order(order_id=order_id,data=order_data)
    notification_datetime = datetime.combine(datetime.today(), last_notification_time.time()) - timedelta(minutes=120)
    notification_datetime = notification_datetime.time()
    # Создайте задачу по расписанию
    scheduler.add_job(
        send_email_to_client,  # Передаем ссылку на функцию
        args=[email_data],  # Передаем аргументы в виде списка
        trigger=IntervalTrigger(minutes=30),
        max_instances=1,
        start_date=notification_datetime,
        end_date=last_notification_time.time(),
        id=f"order_{order_id}_notification"
    )
    return {Messages.message: constants.Messages.pr_sent_to_cus}


# All routes for unsuitable place
@router.get("/{place_id}/place")
async def get_place_by_id(
    place_id: str, current_user: DBUser = Depends(get_current_user)
):
    check_role_access(current_user.role, [Roles.manager])
    result = await get_unsuitable_place_by_id(place_id)

    return result


@router.get("/", response_model=list)
async def all_unsuitable_place(current_user: DBUser = Depends(get_current_user)):
    check_role_access(current_user.role, [Roles.manager])
    res = await get_all_data_from_collection()

    return res


@router.post("/unsuitable_place")
async def unsuitable_place(
    files: Annotated[list[UploadFile], File(...)],
    data: UnsuitablePlace = Depends(UnsuitablePlace),
    current_user: DBUser = Depends(get_current_user),
):
    check_role_access(current_user.role, [Roles.warehouseman])
    data = data.dict()
    place_root_path = (
        str(data["row"]) + "-" + str(data["shelf"]) + "-" + str(data["floor"])
    )
    # print("place_path",place_root_path,"\n")
    file_paths = upload_files_for_place(files, place_root_path)
    print("file_paths", file_paths, "\\n")
    data["username"] = current_user.firstname
    data["user_role"] = current_user.role
    data["images"] = file_paths

    await create_unsuitable_place(data)

    return {Messages.success: "created place!"}


@router.put("/invoice_unsuitable_place")
async def invoice_for_products_in_unsuitable_place(
    invoice_data: InvoiceUnsuitablePlace,
    current_user: DBUser = Depends(get_current_user),
):
    check_role_access(current_user.role, [Roles.manager])
    invoice_data.dict()
    row = int(invoice_data.row)
    shelf = int(invoice_data.shelf)
    floor = int(invoice_data.floor)
    await change_location_status(row, shelf, floor)
    temporary_location = {
        "product_id_lists": invoice_data.product_id_list,
        "place_location": invoice_data.temproary_place,
        "status": "to pack",
        Products.timestamp: datetime.now(),
        "responsible_workers": invoice_data.responsible_workers,
    }
    await temporarily_place(temporary_location)
    temporary_location = {
        "temporary_location": invoice_data.temproary_place,
        Products.status: "unalocated_product",
        Users.user_id: current_user.id,
    }
    await update_many_products(invoice_data.product_id_list, temporary_location)

    # pass
    return {"message": "successful invoiced"}


# End user work
@router.put("/{order_id}/done_task")
async def report_every_employee(
    order_id: str,
    report: CompanyUpdateInfo,
    current_user: DBUser = Depends(get_current_user),
):
    roles = [
        Roles.dispatcher,
        Roles.controller,
        Roles.employee,
        Roles.loader,
        Roles.manager,
        Roles.warehouseman,
        Roles.salesman,
        Roles.workWOMEN,
    ]
    check_role_access(current_user.role, roles)
    report_data = report.dict()
    report_data["user_id"] = current_user.id
    report_data["order_id"] = order_id
    await service.create_every_employee_report(report_data)
