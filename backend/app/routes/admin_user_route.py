from fastapi import APIRouter, status, HTTPException, Depends
from app.schemas.user_schemas import UserSignup, UserLogin
from app.enum.role_enum import RoleName
from app.cruds.user_cruds import (
    get_user_by_email,
    create_user,
    verify_user_password,
    get_user_by_id,
    update_password,
)
from pymongo.errors import PyMongoError
from app.auth.jwt_handler import admin_sign_jwt
from datetime import datetime, timezone
from app.auth.auth import get_user_from_refresh_token, get_admin_user

router = APIRouter()


@router.post("/signup")
async def signup(user_data: UserSignup, role: RoleName):
    try:
        existing_user = await get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = await create_user(user_data, role)  # assume this already has checks
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed",
            )
        return {"msg": "Signup successful", "user": user}

    except HTTPException as http_exc:
        raise http_exc

    except PyMongoError as db_exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during signup",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.post("/login")
async def login(user_data: UserLogin):
    try:
        if not user_data.email or not user_data.password:
            raise HTTPException(
                status_code=422, detail="Email and password are required"
            )
        user = await get_user_by_email(user_data.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user and await verify_user_password(user, user_data.password):
            user.last_login = datetime.now(
                timezone.utc
            )  # Set last_login to current UTC time
            await user.save()
            token = await admin_sign_jwt(str(user.id), user.email)
            return {"msg": "Login succesful", "user": user, "token": token}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException as http_exc:
        raise http_exc  # Let FastAPI handle known errors

    except PyMongoError as db_err:
        raise HTTPException(status_code=500, detail="Database error during login")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error during login"
        )


@router.get("/get_access_token_from_refresh_token")
async def get_access_token_from_refresh_token(
    current_user: dict = Depends(get_user_from_refresh_token),
):
    try:
        user_id = current_user.get("user_id")
        email = current_user.get("email_id")
        if user_id and email:
            token = await admin_sign_jwt(user_id, email)
            return {"msg": "Token Renewed Successfully", "token": token}
        else:
            raise HTTPException(status_code=404, detail="User not found")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error during login"
        )


@router.get("/reset_password")
async def reset_password(
    old_password: str, new_password: str, current_user: dict = Depends(get_admin_user)
):
    try:
        user_id = current_user.get("user_id")
        user = await get_user_by_id(user_id)
        if user and await verify_user_password(user, old_password):
            response = await update_password(user_id, new_password)
            if response:
                return {"msg": "Password Updated Successfully"}
            else:
                return {"msg": "User not Found"}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error during login"
        )
