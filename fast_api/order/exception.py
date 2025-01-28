from ..exceptions import NotFound,AllReadyExists,DoesNotExist
from .constants import Messages

class OrderNotFoundById(NotFound):
    DETAIL = Messages.order_not_found_by_id

class NoProductInOrder(NotFound):
    DETAIL = Messages.poduct_by_name