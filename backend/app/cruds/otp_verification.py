from datetime import timedelta, timezone
from typing import Optional

import httpx
from app.models.otp_verification import OtpVerification
from app.utils.datetime import utc_now
from app.utils.error_handling import SQLError, get_error_messages
import random

otp_errors = get_error_messages("otp_verification")


def generate_otp():
    return f"{random.randint(100000, 999999)}"


async def create_or_update_otp_entry(data, thread_id: str = None):
    try:
        now = utc_now()
        valid_until = now + timedelta(minutes=1)
        cooldown_until = now + timedelta(hours=1)
        existing = await OtpVerification.find_one(
            OtpVerification.country_code == "91",
            OtpVerification.thread_id == thread_id,
            OtpVerification.contact_no == data.contact_no,
            OtpVerification.is_verified == False,
            OtpVerification.is_deleted == False,
        )
        if existing:
            # Ensure 'resend_cooldown_until' is timezone-aware
            if (
                existing.resend_cooldown_until
                and existing.resend_cooldown_until.tzinfo is None
            ):
                existing.resend_cooldown_until = existing.resend_cooldown_until.replace(
                    tzinfo=timezone.utc
                )

            # Ensure 'valid_until' is timezone-aware if needed
            if existing.valid_until and existing.valid_until.tzinfo is None:
                existing.valid_until = existing.valid_until.replace(tzinfo=timezone.utc)

            if existing.resend_attempts >= existing.max_resend_attempts:
                if (
                    existing.resend_cooldown_until
                    and now < existing.resend_cooldown_until
                ):
                    return {
                        "message": "Try later. Maximum attempts reached.",
                        "detail": otp_errors["RESEND_LIMIT_REACHED"],
                    }
                existing.resend_attempts = 0

            existing.otp_code = generate_otp()
            existing.resend_attempts += 1
            existing.valid_until = valid_until
            existing.resend_cooldown_until = cooldown_until
            await existing.save()
            return existing.to_json_dict()

        new_otp = OtpVerification(
            country_code="91",
            thread_id=thread_id,
            contact_no=data.contact_no,
            name=data.name,
            otp_code=generate_otp(),
            valid_until=valid_until,
            resend_cooldown_until=cooldown_until,
        )
        await new_otp.insert()
        return new_otp.to_json_dict()
    except SQLError as e:
        raise e
    except Exception as e:
        raise SQLError(message=str(e), detail=otp_errors["UNEXPECTED_ERROR_SENDING"])


async def verify_otp_entry(data, thread_id: str = None):
    try:
        # Step 1: Find matching OTP record
        record = await OtpVerification.find_one(
            OtpVerification.thread_id == thread_id,
            OtpVerification.country_code == "91",
            OtpVerification.contact_no == data.contact_no,
            OtpVerification.otp_code == data.otp_code,
            OtpVerification.is_verified == False,
            OtpVerification.is_deleted == False,
        )

        if not record:
            record = await OtpVerification.find_one(
                OtpVerification.thread_id == thread_id,
                OtpVerification.country_code == "91",
                OtpVerification.contact_no == data.contact_no,
                OtpVerification.otp_code == data.otp_code,
                OtpVerification.is_verified == True,
                OtpVerification.is_deleted == False,
            )
            if record:
                response = record.to_json_dict()
                return response["is_verified"]

            else:
                raise SQLError(
                    message="OTP not found.",
                    detail=otp_errors["OTP_VERIFICATION_FAILED"],
                )

        # Step 2: Validate expiration
        if record.valid_until.tzinfo is None:
            record_valid_until = record.valid_until.replace(tzinfo=timezone.utc)
        else:
            record_valid_until = record.valid_until

        if utc_now() > record_valid_until:
            return {"message": "OTP expired.", "detail": otp_errors["EXPIRED_OTP"]}

        # Step 3: Mark as verified
        record.is_verified = True
        await record.save()

        # 🧠 IVF API call (separated)
        # await call_ivf_lead_creation_api(full_name=data.name or "Unknown", contact_no=data.contact_no)# raise error for 4xx or 5xx

        # Step 6: Return success response
        response = record.to_json_dict()
        return response["is_verified"]

    except httpx.HTTPStatusError as e:
        return False
    except SQLError as e:
        return False
    except Exception as e:
        return False


async def send_indira_otp(contact_no: str, otp_code: str):
    try:
        # Construct the message with the OTP code
        message = f"Your OTP from Indira IVF is: {otp_code}"

        # Build the URL with query parameters
        url = (
            f"https://sms.fabmediatech.com/api/SmsApi/SendMultipleApi"
            f"?UserID=indiraivfapi"
            f"&Password=heon3641HE"
            f"&SenderID=INDIVF"
            f"&EntityID=1601100000000005185"
            f"&Phno={contact_no}"
            f"&Msg={message}"
        )

        # Make the request
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)

        # Handle the response
        if response.status_code != 200:
            raise SQLError(
                detail="OTP sending failed",
                message=f"OTP API responded with status {response.status_code}: {response.text}",
            )

        return response.json()

    except SQLError as e:
        raise e
    except httpx.RequestError as e:
        raise SQLError(detail="OTP request failed", message=str(e))


async def call_ivf_lead_creation_api(
    full_name: str, contact_no: str, pincode: Optional[str] = "580024"
):
    try:

        payload = {
            "last_name": full_name,
            "mobile": contact_no,
            "lead_status": "New",
            "lead_sub_status": "New",
            "pincode": pincode,
            "enquiry_source": "Digital",
            "enquiry_source_sub_type": "Organic Website Chatbot",
        }

        url = "https://xpiuat.indiraivf.in/magicxpi/MgWebRequester.dll"
        params = {
            "appname": "IFSsfdc",
            "prgname": "HTTP",
            "arguments": "-Ahttp_sfdc%23success_calculator",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, params=params, json=payload)
            response.raise_for_status()

        return response.json()

    except httpx.HTTPStatusError as e:
        raise SQLError(message="IVF api failed", detail="An unexpected error occured")
    except httpx.RequestError as e:
        return "Timeout issue"
    except Exception as e:
        raise SQLError(
            message="Unexpected error in IVF API", detail="An unexpected error occured"
        )
