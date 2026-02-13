from fastapi import APIRouter, Depends
from app.models.user_info import User_Info
from app.schemas.user_information import UserInformation
from fastapi import HTTPException
from app.auth.auth import get_current_user
from app.models.user_info import UserFeedback
from app.core.email_send import send_approval_email
import random, string

router = APIRouter()


@router.post("/insert_user_info")
async def insert_user_info(
    user_info: UserInformation,
    thread_id: str,
    current_user: dict = Depends(get_current_user),
):
    try:
        if thread_id:
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            if user:
                user.name = user_info.firstName
                user.phone_number = user_info.mobile
                user.email_id = user_info.email
                user.pincode = user_info.pincode
                user.employment_type = user_info.employmentType
                user.user_address = user_info.address
                user.preffered_center_address = user_info.treatmentLocation
                user.State = user_info.state
                user.pan_number = user_info.pan
                user.aadhar_number = user_info.aadhar

                await user.save()
                await send_approval_email(user, thread_id, "12345")
            else:
                new_user = User_Info(
                    name=user_info.firstName,
                    phone_number=user_info.mobile,
                    email_id=user_info.email,
                    pincode=user_info.pincode,
                    employment_type=user_info.employmentType,
                    user_address=user_info.address,
                    preffered_center_address=user_info.treatmentLocation,
                    State=user_info.state,
                    pan_number=user_info.pan,
                    aadhar_number=user_info.aadhar,
                    thread_id=thread_id,
                )
                await new_user.insert()
                await send_approval_email(new_user, thread_id, "12345")
            return {
                "status_code": 200,
                "message": "User information inserted successfully",
            }
        else:
            raise HTTPException(status_code=400, detail="thread_id is required")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/update_feedback")
async def update_user_feedback(
    thread_id: str,
    feedback_status: UserFeedback,
    current_user: dict = Depends(get_current_user),
):
    try:
        user = await User_Info.find_one(User_Info.thread_id == thread_id)
        if user:
            user.user_feedback = feedback_status.value
            await user.save()
        else:
            user = User_Info(user_feedback=feedback_status.value, thread_id=thread_id)
            await user.insert()
        return {"status_code": 200, "message": "User Feedback inserted successfully"}

    except HTTPException:
        # Let FastAPI handle it correctly (400/404/etc.)
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# @router.get("/generate_reference_number")
# async def generate_reference_number(current_user:dict=Depends(get_current_user)):
#     try:
#         prefix = ''.join(random.choices(string.ascii_uppercase, k=2))  # 2 random letters
#         middle = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))  # 9 alphanumeric
#         reference_number = f"{prefix}{middle}"
#         return {"reference_number": reference_number}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal server error")
