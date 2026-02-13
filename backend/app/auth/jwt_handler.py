from fastapi import HTTPException, status
import time
from typing import Dict
import jwt
from app.utils.config import ENV_PROJECT
from jwt import ExpiredSignatureError, InvalidTokenError
import uuid


def generate_session_id() -> str:
    try:
        session_id = str(uuid.uuid4())
        if not session_id:
            raise ValueError("Failed to generate a valid UUID")
        return session_id
    except ValueError as ve:
        raise HTTPException(status_code=500, detail="Invalid session ID generated")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate session ID")


def guest_token_response(token: str):
    """
    Create a dictionary response containing the access token.

    Args:
        token (str): The access token.

    Returns:
        dict: A dictionary response with the access token.

    """
    try:
        if not token or not isinstance(token, str):
            raise HTTPException(status_code=422, detail="Invalid token")
        token = "Bearer" + " " + token
        return {"access_token": token}
    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail="Error creating token response")


def guest_sign_jwt(user_id: str) -> Dict[str, str]:
    """
    Sign a JWT token for the given user ID.

    Args:
        user_id (str): The user ID to include in the JWT payload.

    Returns:
        Dict[str, str]: A dictionary response containing the access token.

    """
    try:
        if not user_id or not isinstance(user_id, str):
            raise HTTPException(status_code=422, detail="Invalid user ID for JWT")
        session_id = generate_session_id()
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "expires": time.time()
            + (
                ENV_PROJECT.GUEST_TOKEN_EXPIRY_DAYS
                * ENV_PROJECT.GUEST_TOKEN_EXPIRY_SECONDS
            ),
        }
        return guest_token_response(
            jwt.encode(payload, ENV_PROJECT.GUEST_TOKEN_SECRET_KEY, algorithm="HS256")
        )
    except jwt.PyJWTError as jwt_err:
        raise HTTPException(status_code=500, detail="Token generation failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


def update_jwt(user_id: str, thread_id: str, session_id: str) -> Dict[str, str]:
    """
    Sign a JWT token for the given user ID.

    Args:
        user_id (str): The user ID to include in the JWT payload.

    Returns:
        Dict[str, str]: A dictionary response containing the access token.

    """
    try:
        if not all([user_id, thread_id, session_id]):
            raise ValueError("Missing one or more required fields for JWT payload")
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "thread_id": thread_id,
            "expires": time.time()
            + (
                ENV_PROJECT.GUEST_TOKEN_EXPIRY_DAYS
                * ENV_PROJECT.GUEST_TOKEN_EXPIRY_SECONDS
            ),
        }
        return guest_token_response(
            jwt.encode(payload, ENV_PROJECT.SECRET_KEY, algorithm="HS256")
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve)
        )

    except jwt.PyJWTError as jwt_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token generation failed",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while generating token",
        )


def decode_jwt(token: str, secret_key: str) -> dict:
    """
    Decode a JWT token and return the decoded payload if the token is valid.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: The decoded JWT payload if the token is valid, None if invalid or expired.
    """
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])

        if "expires" in decoded_token and decoded_token["expires"] >= time.time():
            return decoded_token
        else:
            return None

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error decoding token",
        )


async def admin_token_response(access_token: str, refresh_token: str) -> Dict[str, str]:
    """
    Create a dictionary response containing both access and refresh tokens.
    """
    try:
        if not access_token or not isinstance(access_token, str):
            raise HTTPException(status_code=422, detail="Invalid access token")
        if not refresh_token or not isinstance(refresh_token, str):
            raise HTTPException(status_code=422, detail="Invalid refresh token")

        return {
            "access_token": f"Bearer {access_token}",
            "refresh_token": f"Bearer {refresh_token}",
            "token_type": "bearer",
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise HTTPException(status_code=500, detail="Error creating token response")


async def admin_sign_jwt(user_id: str, email_id: str) -> Dict[str, str]:
    """
    Sign both access and refresh JWT tokens for the given user ID.
    """
    try:
        if not user_id or not isinstance(user_id, str):
            raise HTTPException(status_code=422, detail="Invalid user ID for JWT")

        # --- Access token ---
        access_payload = {
            "user_id": user_id,
            "email_id": email_id,
            "type": "access",
            "expires": time.time()
            + (
                ENV_PROJECT.GUEST_TOKEN_EXPIRY_DAYS
                * ENV_PROJECT.GUEST_TOKEN_EXPIRY_SECONDS
            ),
        }

        # --- Refresh token ---
        refresh_payload = {
            "user_id": user_id,
            "email_id": email_id,
            "type": "refresh",
            "expires": time.time()
            + (
                ENV_PROJECT.REFRESH_TOKEN_EXPIRY_DAYS
                * ENV_PROJECT.GUEST_TOKEN_EXPIRY_SECONDS
            ),
        }

        access_token = jwt.encode(
            access_payload, ENV_PROJECT.ADMIN_SECRET_KEY, algorithm="HS256"
        )
        refresh_token = jwt.encode(
            refresh_payload, ENV_PROJECT.ADMIN_REFRESH_SECRET_KEY, algorithm="HS256"
        )

        return await admin_token_response(access_token, refresh_token)

    except jwt.PyJWTError:
        raise HTTPException(status_code=500, detail="Token generation failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
