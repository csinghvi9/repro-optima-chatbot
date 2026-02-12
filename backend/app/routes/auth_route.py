from fastapi import APIRouter, HTTPException
from app.auth.jwt_handler import guest_sign_jwt

router = APIRouter()


@router.get("/guest_token")
async def guest_token():
    try:
        token = guest_sign_jwt("guest")
        return {"msg": "Guest token generated", "token": token}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error during guest token generation",
        )
