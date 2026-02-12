from app.utils.llm_utils import ask_openai_validation_assistant
from app.models.threads import Thread
from app.models.user_info import User_Info
from app.core.ivf_centers import find_nearest_by_postal, find_pincode_by_city_name
from bson import ObjectId
import json
import re
from app.core.existingUser import step_check
from app.schemas.otp_verification import OtpRequest, OtpVerify
from app.cruds.otp_verification import (
    create_or_update_otp_entry,
    send_indira_otp,
    verify_otp_entry,
    call_ivf_lead_creation_api,
)
import ast
from app.core.format_check import validate_answer


async def FindHospital(
    thread_id: str, flow_id: str, step_id: str, language: str, user_message: str
):
    find_hospital_flow = {
        "flow_id": "cost_and_package",
        "steps": {
            "1": {
                "step_id": "1",
                "message": [
                    "To share the IVF Centers details, I’ll need a few quick details from you",
                    "Please share your pincode or city name",
                ],
                "expected_input": "user wants to find nearby ivf or indira ivf centers",
                "valid_condition": "",
                "action": None,
                "other_text": "",
                "final_text": "",
                "next_step": "2",
            },
            "2": {
                "step_id": "2",
                "message": "",
                "expected_input": "pincode or city or area name",
                "valid_condition": r"^[A-Za-z\s]{2,50}$",
                "action": "send_center details",
                "other_text": [
                    " Please enter a valid pincode or city name  to check clinic availability near you",
                ],  # "Please share your name it is important for appointment booking step",
                "final_text": [
                    "We cannot proceed with the process without these details. Please share your pincode to continue",
                    "You can enter your city name instead",
                ],
                "next_step": "3",
            },
            "3": {
                "step_id": "3",
                "message": [
                    "",
                    "Hope this was helpful. Let me know if you need more info",
                ],
                "expected_input": "center_selection",
                "valid_condition": r".+",
                "action": None,
                "other_text": "",
                "final_text": "",
                "next_step": None,
            },
        },
    }

    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)
    step_count = thread.step_count

    if thread and thread.step_id:
        step_id = thread.step_id
    elif not step_id:
        step_id = "1"
        user_message = "Find Indira IVF Centers near me?"

    step = find_hospital_flow["steps"].get(step_id)
    if not step:
        return {"error": "Invalid step"}

    if not user_message or user_message.strip() == "":
        user_message = ""

    if step["step_id"] == "2":
        match = re.search(r"\b\d{6}\b", user_message)
        words = user_message.split()
        if match:
            pincode = match.group(0)  # the actual 6-digit code
            response = await find_nearest_by_postal(pincode, "pincode")
            if len(response) == 0:
                if language == "English":
                    return step["other_text"], "invalid_feedback"
                else:
                    prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['other_text']} OUTPUT_FORMAT:list"
                    llm_answer = await ask_openai_validation_assistant(prompt)
                    try:
                        llm_json = json.loads(llm_answer)
                    except:
                        try:
                            llm_json = ast.literal_eval(llm_answer)
                        except:
                            llm_json = [llm_answer]
                    is_validated, answer = await validate_answer(
                        llm_json, step["other_text"], language
                    )
                    if is_validated:
                        return llm_json, "invalid_feedback"
                    else:
                        return answer, "out_of_context"
        # pass only the pincode
        elif len(words) == 1 and language == "English":
            response = await find_nearest_by_postal(user_message, "city")
            if len(response) == 0:
                return step["other_text"], "invalid_feedback"
            pincode = await find_pincode_by_city_name(user_message)

        else:
            prompt = f"Your work is to give the city name from this text:{user_message} if it is in another language other than english then convert city name in english and if there is no city name then return None and If the user refuses to give location information (for example: 'I don’t want to share', 'not sure', 'skip', 'no', 'none'), return Invalid. don't give any text from your own only None,Cityname"
            city_name = await ask_openai_validation_assistant(prompt)
            if city_name != "None" and city_name != "Invalid":
                response = await find_nearest_by_postal(city_name, "city")
                if len(response) == 0:
                    if language == "English":
                        return step["other_text"], "invalid_feedback"
                    else:
                        prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['other_text']} OUTPUT_FORMAT:list"
                        llm_answer = await ask_openai_validation_assistant(prompt)
                        try:
                            llm_json = ast.literal_eval(llm_answer)
                        except:
                            try:
                                llm_json = ast.literal_eval(llm_answer)
                            except:
                                llm_json = [llm_answer]
                        is_validated, answer = await validate_answer(
                            llm_json, step["other_text"], language
                        )
                        if is_validated:
                            return llm_json, "invalid_feedback"
                        else:
                            return answer, "out_of_context"

                pincode = await find_pincode_by_city_name(city_name)
            elif city_name in ["Invalid", "invalid"]:
                if language == "English":
                    return step["final_text"], "invalid_feedback"
                else:
                    prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['final_text']} OUTPUT_FORMAT:list"
                    try:
                        llm_json = ast.literal_eval(llm_answer)
                    except:
                        try:
                            llm_json = ast.literal_eval(llm_answer)
                        except:
                            llm_json = [llm_answer]
                    return llm_json, "invalid_feedback"

            else:
                if language == "English":
                    return step["other_text"], "invalid_feedback"
                else:
                    prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['final_text']} OUTPUT_FORMAT:list"
                    llm_answer = await ask_openai_validation_assistant(prompt)
                    try:
                        llm_json = ast.literal_eval(llm_answer)
                    except:
                        try:
                            llm_json = ast.literal_eval(llm_answer)
                        except:
                            llm_json = [llm_answer]
                    is_validated, answer = await validate_answer(
                        llm_json, step["final_text"], language
                    )
                    if is_validated:
                        return llm_json, "invalid_feedback"
                    else:
                        return answer, "out_of_context"

        if response:
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            if user:
                user.preffered_center = response
                user.pincode = pincode
                await user.save()
            else:
                user_info = User_Info(
                    preffered_center=response, pincode=pincode, thread_id=thread_id
                )
                await user_info.insert()
            next_step = step["next_step"]
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            if thread:
                thread.flow_id = flow_id
                thread.step_id = next_step
                thread.previous_flow = thread.flow_id
                thread.previous_step = step["step_id"]
                await thread.save()
                return response, "centers"
        else:
            if language == "English":
                return step["other_text"], "invalid_feedback"
            else:
                prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['other_text']} OUTPUT_FORMAT:list"
                llm_answer = await ask_openai_validation_assistant(prompt)
                try:
                    llm_json = json.loads(llm_answer)
                except:
                    try:
                        llm_json = ast.literal_eval(llm_answer)
                    except:
                        llm_json = [llm_answer]
                is_validated, answer = await validate_answer(
                    llm_json, step["other_text"], language
                )
                if is_validated:
                    return llm_json, "invalid_feedback"
                else:
                    return answer, "out_of_context"

    if step["step_id"] == "3":
        user = await User_Info.find_one(User_Info.thread_id == thread_id)
        for c in user.preffered_center:
            if (c["Clinic Name"].strip().lower() == user_message.strip().lower()) or (
                c["Clinic Name"].strip().lower().split("-")[1].strip()
                == user_message.strip().lower()
            ):
                user.preffered_center_address = c["Address"]
                user.City = c["City"]
                user.State = c["State"]
                await user.save()
                step["message"][0] = c["Clinic Name"] + "-" + c["Address"]
        if step["message"][0] == "":
            match = re.search(r"\b\d{6}\b", user_message)
            words = user_message.split()
            other_text = [
                " Please enter a valid pincode or city name  to check clinic availability near you",
            ]
            if match:
                pincode = match.group(0)  # the actual 6-digit code
                response = await find_nearest_by_postal(pincode, "pincode")
            # pass only the pincode
            elif len(words) == 1 and language == "English":
                response = await find_nearest_by_postal(user_message, "city")
                if len(response) == 0:
                    return other_text, "invalid_feedback"
                pincode = await find_pincode_by_city_name(user_message)

            else:
                prompt = f"Your work is to give the city name from this text:{user_message} if it is in another language other than english then convert city name in english and if there is no city name then return None and If the user refuses to give location information (for example: 'I don’t want to share', 'not sure', 'skip', 'no', 'none'), return Invalid. don't give any text from your own only None,Cityname"
                city_name = await ask_openai_validation_assistant(prompt)
                if city_name != "None" and city_name != "Invalid":
                    response = await find_nearest_by_postal(city_name, "city")
                    if len(response) == 0:
                        if language == "English":
                            return other_text, "invalid_feedback"
                        else:
                            prompt = f"Yo have to just return {other_text} in translated langauage-{language} Output:as Json and in same structure like the message which i have given"
                            llm_answer = await ask_openai_validation_assistant(prompt)
                            try:
                                llm_json = json.loads(llm_answer)
                            except:
                                llm_json = [llm_answer]
                            is_validated, answer = await validate_answer(
                                llm_json, step["other_text"], language
                            )
                            if is_validated:
                                return llm_json, "invalid_feedback"
                            else:
                                return answer, "out_of_context"

                    pincode = await find_pincode_by_city_name(city_name)
                else:
                    if language == "English":
                        return other_text, "invalid_feedback"
                    else:
                        prompt = f"You have to just return {other_text} in translated langauage-{language} Output:as list and in same structure like the message which i have given"
                        llm_answer = await ask_openai_validation_assistant(prompt)
                        try:
                            llm_json = ast.literal_eval(llm_answer)
                        except:
                            llm_json = [llm_answer]
                        is_validated, answer = await validate_answer(
                            llm_json, step["other_text"], language
                        )
                        if is_validated:
                            return llm_json, "invalid_feedback"
                        else:
                            return answer, "out_of_context"

            if response:
                user = await User_Info.find_one(User_Info.thread_id == thread_id)
                if user:
                    user.preffered_center = response
                    user.pincode = pincode
                    await user.save()
                else:
                    user_info = User_Info(
                        preffered_center=response, pincode=pincode, thread_id=thread_id
                    )
                    await user_info.insert()
                next_step = step["next_step"]
                user = await User_Info.find_one(User_Info.thread_id == thread_id)
                return response, "centers"
            else:
                if language == "English":
                    return other_text, "invalid_feedback"
                else:
                    prompt = f"You have to just return {other_text} in translated langauage-{language} Output:as list and in same structure like the message which i have given"
                    llm_answer = await ask_openai_validation_assistant(prompt)
                    try:
                        llm_json = ast.literal_eval(llm_answer)
                    except:
                        llm_json = [llm_answer]
                    is_validated, answer = await validate_answer(
                        llm_json, step["other_text"], language
                    )
                    if is_validated:
                        return llm_json, "invalid_feedback"
                    else:
                        return answer, "out_of_context"
    prompt = f"""
You are a validation assistant.
Conversation language = {language}.
Step: {step_id}, Expecting: {step['expected_input']}
the expected input can also be in user selected language also 
User input: "{user_message}"
Valid condition (regex): {step['valid_condition']}
bot_response must ALWAYS be written in {language}, regardless of input language or system language.



Instructions:
1. Refusal detection:
   - If the {user_message} intent states that it dosen't want to share information then return only {step['final_text']} (translated into {language}), with status = "INVALID".
   - If user input clearly expresses **refusal** (like "I don’t want to give", "skip", "no", "nahi batana", "not sharing", "prefer not to say"),
     then → return only {step['final_text']} (translated into {language}), with status = "INVALID".
   - Do NOT treat unrelated or invalid inputs as refusal.
2. Regex + meaning validation:
   - If the input matches {step['valid_condition']} (regex + meaning check), 
     then → return status = "VALID" and bot_response = {step['message']} (translated into {language}).
3. Otherwise:
   - If input is not refusal and does not match regex, 
     then → return status = "INVALID" and bot_response = {step['other_text']} (translated into {language}).

- ** and also in same the format if it is string then string and if its is list of string then list of string

Format:
{{
  "status": "VALID" or "INVALID",
  "bot_response": "string or list of string  (next message to show the user in {language})"
}}

***IMPOTANT***-Always return response in the above format only

Rules:
- If regex + meaning are correct → status = "VALID" and bot_response = next step message (filled with variables if available).
- If not valid → status = "INVALID" and bot_response = re-ask current step politely in {language}.
"""

    llm_answer = await ask_openai_validation_assistant(prompt)

    try:
        llm_json = json.loads(llm_answer)
    except Exception:
        try:
            llm_json = ast.literal_eval(llm_answer)
        except Exception:
            llm_json = {"status": "INVALID", "bot_response": step["message"]}

    is_validated, answer = await validate_answer(
        llm_json, {"status": "INVALID", "bot_response": step["message"]}, language
    )
    if not (is_validated):
        is_validated, answer = await validate_answer(
            llm_json,
            {"status": "INVALID", "bot_response": step["other_text"]},
            language,
        )
        if not (is_validated):
            is_validated, answer = await validate_answer(
                llm_json,
                {"status": "INVALID", "bot_response": step["final_text"]},
                language,
            )
            if not (is_validated):
                return answer, "out_of_context"
    # Final decision
    if llm_json.get("status") == "INVALID":
        if thread:
            thread.step_count += 1
            await thread.save()

    if llm_json.get("status") == "VALID":
        next_step = step["next_step"]

        # Save thread
        if thread:
            thread.flow_id = flow_id
            thread.step_id = next_step
            thread.step_count = 1
            thread.previous_flow = thread.flow_id
            thread.previous_step = step["step_id"]
            await thread.save()
        if step["step_id"] == "3":
            return llm_json.get("bot_response"), "feedback"
        else:
            return llm_json.get("bot_response"), None
    else:
        # stay on same step
        if thread and step["step_id"] == "1":
            next_step = step["next_step"]
            thread.flow_id = flow_id
            thread.step_id = next_step
            thread.step_count = 1
            thread.previous_flow = thread.flow_id
            thread.previous_step = step["step_id"]
            await thread.save()
        if step["step_id"] == "2" and isinstance(llm_json.get("bot_response"), list):
            return llm_json.get("bot_response"), "invalid_feedback"
        return llm_json.get("bot_response"), None
