from json import JSONDecodeError
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware


class SQLError(Exception):
    def __init__(self, message: str, detail: str = None, status_code: int = 500):
        self.message = message
        self.detail = detail
        self.status_code = status_code
        super().__init__(message)

    def as_response(self):
        return JSONResponse(
            status_code=self.status_code,
            content={
                "success": False,
                "result": None,
                "error_message": self.message,
                "error_detail": self.detail,
                "statusCode": self.status_code,
            },
        )


class JWTError(Exception):
    def __init__(self, message: str, detail: str = None, status_code: int = 401):
        self.message = message
        self.detail = detail
        self.status_code = status_code
        super().__init__(message)

    def as_response(self):
        return JSONResponse(
            status_code=self.status_code,
            content={
                "success": False,
                "result": None,
                "error_message": self.message,
                "error_detail": self.detail,
                "statusCode": self.status_code,
            },
        )


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "result": None,
                    "error_message": exc.detail,
                    "error_detail": exc.detail,
                    "statusCode": exc.status_code,
                },
            )
        except JSONDecodeError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "result": None,
                    "error_message": "JSON decode error",
                    "error_detail": str(exc),
                    "statusCode": 422,
                },
            )
        except RequestValidationError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "result": None,
                    "error_message": exc.errors(),
                    "statusCode": 422,
                },
            )
        except SQLError as exc:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "result": None,
                    "error_message": exc.message,
                    "error_detail": exc.detail,
                    "statusCode": 500,
                },
            )
        # except SQLAlchemyError as exc:
        #     return JSONResponse(
        #         status_code=500,
        #         content={
        #             "success": False,
        #             "result": None,
        #             "error_message": str(exc),
        #             "error_detail": str(exc),
        #             "statusCode": 500,
        #         },
        #     )
        except JWTError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "result": None,
                    "error_message": exc.message,
                    "error_detail": exc.detail,
                    "statusCode": exc.status_code,
                },
            )
        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "result": None,
                    "error_message": str(exc),
                    "error_detail": str(exc),
                    "statusCode": 500,
                },
            )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()

    # ✅ Check for JSON decode error
    json_invalid = next(
        (err for err in errors if err.get("type") == "json_invalid"), None
    )
    if json_invalid:
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "result": None,
                "error_message": json_invalid.get("ctx", {}).get(
                    "error", "Invalid JSON"
                ),
                "error_detail": "JSON decode error",
                "statusCode": 422,
            },
        )

    is_missing_file = any(
        "files" in err["loc"] and err["type"] == "missing" for err in errors
    )
    if is_missing_file:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "result": None,
                "error_message": "The 'files' field is required in the request.",  # ← Same as missing for UX consistency
                "error_detail": "Please upload a file.",
                "statusCode": 400,
            },
        )

    is_invalid_file_type = any(
        "files" in err["loc"] and "Expected UploadFile" in err.get("msg", "")
        for err in errors
    )
    if is_invalid_file_type:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "result": None,
                "error_message": "The 'files' field is required in the request.",  # ← Same as missing for UX consistency
                "error_detail": "Please upload a file.",
                "statusCode": 400,
            },
        )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "result": None,
            "error_message": errors,
            "error_detail": "Validation error",
            "statusCode": 422,
        },
    )


def get_error_messages(entity: str) -> dict:
    # Base messages applicable to all entities
    messages = {
        "NOT_FOUND": f"The requested {entity} could not be found.",
        "ALREADY_DELETED": f"The {entity} has already been deleted.",
        "UNABLE_TO_RETRIEVE": f"Unable to retrieve {entity}s.",
        "FAILED_TO_CREATE": f"Failed to create a new {entity}.",
        "FAILED_TO_UPDATE": f"Failed to update the {entity}.",
        "FAILED_TO_DELETE": f"Failed to delete the {entity}.",
        "ALREADY_REGISTERED": f"{entity} with this email is already registered.",
        "UNEXPECTED_ERROR_RETRIEVING": f"An unexpected error occurred while fetching {entity}s.",
        "UNEXPECTED_ERROR_CREATING": f"An unexpected error occurred while creating the {entity}.",
        "UNEXPECTED_ERROR_UPDATING": f"An unexpected error occurred while updating the {entity}.",
        "UNEXPECTED_ERROR_DELETING": f"An unexpected error occurred while deleting the {entity}.",
        "UNEXPECTED_ERROR_SENDING": f"An unexpected error occurred while sending the {entity}.",
        "UNEXPECTED_ERROR_VERIFYING": f"An unexpected error occurred while verifying the {entity}.",
        "PERMISSION_DENIED": f"You do not have permission to access this {entity}.",
        "AUTHENTICATION_FAILED": "Session expired. Please Login.",
        "PROCESSING_FAILED": f"An error occurred while processing the {entity}.",
        "RESEND_LIMIT_REACHED": "You have reached the maximum number of resend attempts. Please try again later.",
        "EXPIRED_OTP": "The OTP has expired. Please request a new one.",
        "OTP_VERIFICATION_FAILED": "OTP verification failed. Please check your OTP and try again.",
    }
    return messages


report_errors = get_error_messages("report")
token_errors = get_error_messages("token")
otp_errors = get_error_messages("otp_verification")
