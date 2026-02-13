from fastapi import APIRouter, Depends
from app.schemas.loan_schemas import LoanUserInformation
from fastapi import HTTPException
from app.auth.auth import get_current_user
from app.models.loan_model import Loan_User
from app.cruds.loan_cruds import generate_reference_number


router = APIRouter()


@router.post("/insert_loan_user_info")
async def insert_loan_user_info(
    loan_info: LoanUserInformation,
    thread_id: str,
    current_user: dict = Depends(get_current_user),
):
    try:
        reference_number = await generate_reference_number()
        if thread_id:
            loan_user = Loan_User(
                name=loan_info.name,
                phone_number=loan_info.phone_number,
                email_id=loan_info.email_id,
                pincode=loan_info.pincode,
                user_address=loan_info.user_address,
                employment_type=loan_info.employment_type,
                state=loan_info.state,
                treatment_location=loan_info.treatment_location,
                pan_number=loan_info.pan_number,
                aadhar_number=loan_info.aadhar_number,
                thread_id=thread_id,
                reference_id=reference_number,
            )

            await loan_user.insert()
            return {
                "status_code": 200,
                "message": "User information inserted successfully",
                "reference_id": reference_number,
            }
        else:
            raise HTTPException(status_code=400, detail="thread_id is required")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
