# Installed packages
from pydantic import BaseModel
from datetime import datetime

# Local packages
from .constants import Errors, Messages


class Success(BaseModel):
    status_code: int = 200
    message: str = Messages.success

    class Config:
        extra = "allow"


class BaseError(BaseModel):
    status_code: int = 500
    message: str = Errors.int_ser_err
    error_code: int = 0
    timestamp: float = datetime.utcnow().isoformat()


class NotFoundError(BaseError):
    status_code: int = 404
    message: str = Errors.not_found
    error_code: int = 0
    timestamp: float = datetime.utcnow().isoformat()


class InvalidCredentials(BaseError):
    status_code: int = 400
    message: str = Errors.invalid_cr
    error_code: int = 0
    timestamp: float = datetime.utcnow().isoformat()


class PermissionsError(BaseError):
    status_code: int = 403
    message: str = Errors.permission
    error_code: int = 0
    timestamp: float = datetime.utcnow().isoformat()


class UnauthorizedError(BaseError):
    status_code: int = 401
    message: str = Errors.not_auth
    error_code: int = 0
    timestamp: float = datetime.utcnow().isoformat()


class DuplicateKeyError(BaseError):
    status_code: int = 208
    message: str = Errors.alr_exists
    error_code: int = 0
    timestamp: float = datetime.utcnow().isoformat()


class ConflictError(BaseError):
    status_code: int = 409
    message: str = Errors.pr_narr
    error_code: int = 0
    timestamp: float = datetime.utcnow().isoformat()


class RequestEntityTooLarge(BaseError):
    status_code: int = 413
    message: str = Errors.large_file
    error_code: int = 0
    timestamp: float = datetime.utcnow().isoformat()


class UnsupportedMediaType(BaseError):
    status_code: int = 415
    message: str = Errors.unsupported_media
    error_code: int = 0
    timestamp: float = datetime.utcnow().isoformat()


class DoesNotExistError(NotFoundError):
    message: str = Errors.doesnt_exist
    error_code: int = 1
    timestamp: float = datetime.utcnow().isoformat()


class AlreadyCheckedError(PermissionsError):
    message: str = Errors.qlty_checked
    error_code: int = 1
    timestamp: float = datetime.utcnow().isoformat()


class QualityCheckFailedError(ConflictError):
    message: str = Errors.qlty_ch_failed
    error_code: int = 1
    timestamp: float = datetime.utcnow().isoformat()


class InvalidIdError(InvalidCredentials):
    message: str = Errors.invalid_id
    error_code: int = 1
    timestamp: float = datetime.utcnow().isoformat()


class EmptyFileUpload(InvalidCredentials):
    message: str = Errors.empty_file
    error_code: int = 1
    timestamp: float = datetime.utcnow().isoformat()


class FileUpload(BaseError):
    message: str = Errors.failed_upload
    error_code: int = 0
    timestamp: float = datetime.utcnow().isoformat()


class TokenInvalid(BaseError):
    message: str = Errors.token_invalid_order_create
    error_code: int = 1
    timestamp: float = datetime.utcnow().isoformat()


class AlreadyAssignedWorker(BaseError):
    message: str = Errors.busy_employee
    error_code: int = 1
    timestamp: float = datetime.utcnow().isoformat()

    def __init__(self, busy_employees):
        self.details = {"busy_employees": busy_employees}


class UserDoesntStarted(BaseError):
    message: str = Errors.dont_started_work
    error_code: int = 1
    timestamp: float = datetime.utcnow().isoformat()


class InconsistentOrder(BaseError):
    status_code: int = 425
    message: str = Errors.order_of_operations_was_broken
    error_code: int = 1
    timestamp: float = datetime.utcnow().isoformat()
