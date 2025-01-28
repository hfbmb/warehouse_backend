from ..exceptions import NotFound,AllReadyExists
from .constants import Messages



class ProductNotFoundByName(NotFound):
    DETAIL = Messages.product_not_found_by_name

class ProductNotFoundById(NotFound):
    DETAIL = Messages.not_found_by_id

class ProductAllReadyExist(AllReadyExists):
    DETAIL = Messages.product_allready_exists

# class 