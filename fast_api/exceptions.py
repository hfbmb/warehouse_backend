# Installed packages
from typing import Any, Dict, Optional
from fastapi import HTTPException,status
from datetime import datetime
# Local packages
from .responses import *

class DetailHttpExceptionn(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Server error"

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)

class PermissionDenided(DetailHttpExceptionn):
    STATUS_CODE = status.HTTP_403_FORBIDDEN
    DETAIL = "Permission denided"
class NotFound(DetailHttpExceptionn):
    STATUS_CODE = status.HTTP_404_NOT_FOUND
    DETAIL ="Not found"

class BadRequest(DetailHttpExceptionn):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    DETAIL ="Bad request"

class AllReadyExists(DetailHttpExceptionn):
    STATUS_CODE = status.HTTP_208_ALREADY_REPORTED
    DETAIL ="Duplicate keys"

class DoesntMatchStatus(DetailHttpExceptionn):
    STATUS_CODE=status.HTTP_403_FORBIDDEN
    DETAIL = "Status doesn't match"

class NotAuthenticated(DetailHttpExceptionn):
    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    DETAIL ="User not authenticated"
    def __init__(self) -> None:
        super().__init__(headers ={"WWW-Authenticate":"Bearer"})




class BaseAPIException(Exception):
    status_code: int = 500
    message: str = "Internal Server Error"
    model = BaseError

    # additional_info = {}

    @classmethod
    def response_model(cls):
        js_response = {
            cls.status_code: {"model": cls.model, "description": cls.message}
        }
        # if len(cls.additional_info)!=0{
        #     js_reponse[cls.additional_info[additional_info]]
        # }
        return js_response


class DuplicateKeyException(BaseAPIException):
    status_code: int = 208
    message: str = "Duplicate Keys"
    model = DuplicateKeyError


class NotFoundException(BaseAPIException):
    status_code: int = 404
    message: str = "Not Found"
    model = NotFoundError


class InvalidCredentialsException(BaseAPIException):
    status_code: int = 400
    message: str = "Bad Request"
    model = InvalidCredentials


class ForbiddenException(BaseAPIException):
    status_code: int = 403
    message: str = "Forbidden"
    model = PermissionError


class UnauthorizedException(BaseAPIException):
    status_code: int = 401
    message: str = "Unauthorized"
    model = UnauthorizedError


class ConflictException(BaseAPIException):
    status_code: int = 409
    message: str = "Conflict"
    model = ConflictError


class RequestEntityTooLargeException(BaseAPIException):
    status_code: int = 413
    message: str = "Request payload is too large"
    model = RequestEntityTooLarge


class UnsupportedMediaTypeException(BaseAPIException):
    status_code: int = 415
    message: str = "Unsupported media type"
    model = UnsupportedMediaType


class PermissionException(ForbiddenException):
    model = PermissionsError


class AlreadyExistsException(DuplicateKeyException):
    model = DuplicateKeyError


class DoesNotExist(NotFoundException):
    model = DoesNotExistError


class AlreadyCheckedException(ForbiddenException):
    model = AlreadyCheckedError


class QualityCheckFailed(ConflictException):
    model = QualityCheckFailedError


class InvalidIdException(InvalidCredentialsException):
    model = InvalidIdError


class EmptyFileUploadException(InvalidCredentialsException):
    model = EmptyFileUpload


class FileUploadException(BaseAPIException):
    model = FileUpload


class TokenInvalidException(BaseAPIException):
    model = TokenInvalid


class AlreadyAssignedException(BaseAPIException):
    model = AlreadyAssignedWorker

    def __init__(self, busy_employees):
        super().__init__(model=self.model)
        self.details = {"busy_employees": busy_employees}


class EmployeeWorkStatus(BaseAPIException):
    model = UserDoesntStarted


class LogicBrokenException(BaseAPIException):
    status_code: int = 425
    model = InconsistentOrder
