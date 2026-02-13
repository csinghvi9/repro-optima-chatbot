from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from app.auth.jwt_handler import decode_jwt
from typing import Optional
from jwt import PyJWTError
from app.utils.config import ENV_PROJECT


api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def extract_token_from_header(auth_header: str) -> str:
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    raise HTTPException(status_code=401, detail="Invalid Authorization header format")


async def get_current_user(authorization: Optional[str] = Depends(api_key_header)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        token = extract_token_from_header(authorization)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or malformed token in header",
            )
        decoded_token = decode_jwt(token, ENV_PROJECT.GUEST_TOKEN_SECRET_KEY)

        if not decoded_token:
            raise HTTPException(status_code=401, detail="Token expired or invalid")

        return decoded_token
    except PyJWTError as jwt_err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to decode token"
        )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal authentication error",
        )


async def get_user_from_refresh_token(
    authorization: Optional[str] = Depends(api_key_header),
):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        token = extract_token_from_header(authorization)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or malformed token in header",
            )
        decoded_token = decode_jwt(token, ENV_PROJECT.ADMIN_REFRESH_SECRET_KEY)

        if not decoded_token:
            raise HTTPException(status_code=401, detail="Token expired or invalid")

        return decoded_token
    except PyJWTError as jwt_err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to decode token"
        )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal authentication error",
        )


async def get_admin_user(authorization: Optional[str] = Depends(api_key_header)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        token = extract_token_from_header(authorization)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or malformed token in header",
            )
        decoded_token = decode_jwt(token, ENV_PROJECT.ADMIN_SECRET_KEY)

        if not decoded_token:
            raise HTTPException(status_code=401, detail="Token expired or invalid")

        return decoded_token
    except PyJWTError as jwt_err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to decode token"
        )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal authentication error",
        )
