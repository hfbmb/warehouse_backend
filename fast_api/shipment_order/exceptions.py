from ..exceptions import NotFound
from .constants import Messages

class ShipmentId(NotFound):
    DETAIL = Messages.shipment_order_id

class ShipmentEmpty(NotFound):
    DETAIL = Messages.empty