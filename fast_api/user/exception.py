from ..exceptions import(NotFound,AllReadyExists,DoesNotExist)
from .constants import Messages

class UserAlreadyExist(AllReadyExists):
    DETAIL = Messages.user_allreay_exists

class UserNotFound(NotFound):
    DETAIL = Messages.user_not_found

# class 

class RolesNotFoundById(NotFound):
    DETAIL ="role not found by this id"

class RoleNotFoundByQuery(NotFound):
    DETAIL ="role not found by this query"

class PermissionNotFoundById(NotFound):
    DETAIL = "permission not found by id"