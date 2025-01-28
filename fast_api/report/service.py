# Installed packages

# Local packages
from ..database import reports_collection
from .constants import Reports
from ..exceptions import AlreadyExistsException
from ..user.service import end_user_work


async def get_reports(product_id: str) -> list:
    reports = reports_collection.find({Reports.product_id: product_id})
    reports_list = []
    async for report in reports:
        report[reports.id] = str(report[Reports.id_])
        reports_list.append(report)

    return reports_list


# async def create_report(report: dict, field):
#     # result = await reports_collection.find_one(
#     #     {Reports.product_id: report[Reports.product_id],
#     #      Reports.user_id: report[Reports.user_id],
#     #      field: {"$exists": True}}
#     # )
#     # if result is None:
#     await reports_collection.insert_one(report)
#     #     raise AlreadyExistsException
#     # else:
#     #     await reports_collection.update_one(
#     #         {Reports.product_id: report[Reports.product_id],
#     #      Reports.user_id: report[Reports.user_id],
#     #      field: {"$exists": True}})


async def create_report(report: dict, field):
    results = await reports_collection.find(
        {Reports.product_id: report[Reports.product_id], field: {"$exists": True}}
    ).to_list(length=100)
    if results:
        raise AlreadyExistsException
    await reports_collection.insert_one(report)


async def create_every_employee_report(report: dict):
    status = report["status"]
    await end_user_work(report["order_id"], report["user_id"], status)
    await reports_collection.insert_one(report)
