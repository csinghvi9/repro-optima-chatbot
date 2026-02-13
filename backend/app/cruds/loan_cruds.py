from fastapi import HTTPException
import string, random


async def generate_reference_number():
    try:
        prefix = "".join(
            random.choices(string.ascii_uppercase, k=2)
        )  # 2 random letters
        middle = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=9)
        )  # 9 alphanumeric
        reference_number = f"{prefix}{middle}"
        return reference_number
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
