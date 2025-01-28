from ..exceptions import AllReadyExists,NotFound
from .constants import Messages,Warehouses
from datetime import datetime

class CompanyAlredyExist(AllReadyExists):
    DETAIL = Messages.company_exists

class CompanyNotFound(NotFound):
    DETAIL = Messages.comp_not_dound

class WarehouseNotFound(NotFound):
    DETAIL = Warehouses.warehouse_not_found
