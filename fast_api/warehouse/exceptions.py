from ..exceptions import NotFound,BadRequest
from ..company.constants import Warehouses

class WarehouseNotFound(NotFound):
    DETAIL = Warehouses.warehouse_not_found

class BoxNotFoundByid(NotFound):
    DETAIL = Warehouses.box_not_found_id

class BoxNotFound(NotFound):
    DETAIL = "box not found by this detail"

class ZoneNotFound(NotFound):
    DETAIL = Warehouses.zone_not_found

class CategoryNotFound(NotFound):
    DETAIL = Warehouses.category_not_Found

class RackNotFound(NotFound):
    DETAIL = Warehouses.rack_not_found

class FloorNotFound(NotFound):
    DETAIL = Warehouses.floor_not_found

class CellNotFound(NotFound):
    DETAIL = Warehouses.cell_not_found

class ConditionNotFound(NotFound):
    DETAIL = Warehouses.condition_not_found

class LengthNotCorrectFloor(BadRequest):
    DETAIL = "too long than the length of the rack"

class WidhtFloorNotCorrect(BadRequest):
    DETAIL = "too long than the width of the rack"

class CellLengthNotCorrect(BadRequest):
    DETAIL = "too long than the length of the floor"

class CellWidthNotCorrect(BadRequest):
    DETAIL ="oo long than the width of the floor"

class BoxIsBusy(BadRequest):
    DETAIL ="this box is busy is not active"