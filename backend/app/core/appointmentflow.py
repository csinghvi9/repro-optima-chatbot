from app.utils.llm_utils import ask_openai_validation_assistant
from app.models.threads import Thread
from app.models.user_info import User_Info, AppointmentStatus
from app.core.ivf_centers import find_nearest_by_postal, find_pincode_by_city_name
from bson import ObjectId
import json
import re
from app.core.cancelReschedule import cancelRescheduleFlow
from app.core.existingUser import step_check

import ast
from app.core.format_check import validate_answer


async def appointment_flow(
    thread_id: str, flow_id: str, step_id: str, language: str, user_message: str
):
    appointmentflow = {
        "flow_id": "book_appointment",
        "steps": {
            "1": {
                "step_id": "1",
                "message": "To book appointment, please share your name ",
                "expected_input": "User wants to book an appointment or book free Consultation and it can ask in any language",
                "valid_condition": "",
                "action": None,
                "other_text": "",
                "final_text": "",
                "next_step": "2",
            },
            "2": {
                "step_id": "2",
                "message": "Thanks. Now please mention your preferred pin code or city name to continue with the booking",
                "expected_input": "name of the person or nick name of the person and can be any name in any language like (miqat,ekal,ellis etc) and a valid name not like abc xyz",
                "valid_condition": r"^[A-Za-z\s]{2,50}$",
                "action": None,
                "other_text": "Sorry, I couldn't recognize that as a name. Could you please re-enter your full name Let's try again",
                "final_text": [
                    "We cannot continue with the booking without your name. Please enter your name to proceed",
                    "You can still explore information without giving your name. Would you like to know about topics below",
                ],
                "next_step": "5",
            },
            "5": {
                "step_id": "5",
                "message": [
                    {
                        "first_text": "Thank you for your query.",
                        "second_text": "Our representative will call you shortly",
                        "third_text": "For any query you can call us on 18003092323",
                    }
                ],
                "expected_input": "pincode",
                "valid_condition": r"^\d{6}$",
                "action": None,
                "other_text": [
                    " Please enter a valid pincode or city name  to check clinic availability near you",
                ],
                "final_text": [
                    "We cannot proceed with the booking process without these details. Please share your pincode to continue",
                    "You can enter your city or area name instead",
                ],
                "next_step": "6",
            },
            "6": {
                "step_id": "6",
                "message": [
                    {
                        "first_text": "To cancel or reschedule your appointment, please contact our call center between 9 AM and 6 PM.",
                        "second_text": "CUSTOMER CARE NUMBER",
                        "phone_number": "18003092323",
                    },
                    "Hope this helps! You can come back anytime to explore  or get more info",
                ],
                "expected_input": "yes or no or cancel or reschedule my appointment ",
                "valid_condition": "",
                "action": "cancel_or_reschedule_appointment",
                "other_text": "Alright, Thank you! Was this helpful?",
                "final_text": "",
                "next_step": None,
            },
        },
    }

    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)

    existing_user = await User_Info.find_one(User_Info.thread_id == thread_id)
    if (
        thread.step_id == "6"
    ):
        message = "i want to reschedule my appointment"
        response, contentType = await cancelRescheduleFlow(thread_id, language, message)
        return response, contentType
    if existing_user and existing_user.appointment_status == AppointmentStatus.BOOKED:
        booked_message = [
            {
                "first_text": "Thank you for booking an appointment!",
                "second_text": "Our representative will call you shortly",
                "third_text": "For any query you can call us on 18003092323",
            }
        ]
        return booked_message, "booked"

    if thread and thread.step_id and not (user_message):
        user_message = await step_check(thread_id, appointmentflow, 5)
        new_thread = await Thread.find_one(Thread.id == thread_obj_id)
        step_id = new_thread.step_id
    elif thread and thread.step_id:
        step_id = thread.step_id
    elif not step_id:
        user_message = await step_check(thread_id, appointmentflow, 5)
        new_thread = await Thread.find_one(Thread.id == thread_obj_id)
        if new_thread.step_id:
            step_id = new_thread.step_id
        else:
            step_id = "1"
            user_message = "I want to Book an Appointment"

    step = appointmentflow["steps"].get(step_id)
    if not step:
        return {"error": "Invalid step"}

    if not user_message or user_message.strip() == "":
        user_message = ""

    if step["step_id"] == "5":
        match = re.search(r"\b\d{6}\b", user_message)
        words = user_message.split()
        if match:
            pincode = match.group(0)  # the actual 6-digit code
            response = True

        else:
            prompt = f"Your work is to give the city name from this text:{user_message} if it is in another language other than english then convert city name in english and if there is no city name then return None and If the user refuses to give location information (for example: 'I don't want to share', 'not sure', 'skip', 'no', 'none'), return Invalid. don't give any text from your own only Noneor Cityname or Invalid"
            city_name = await ask_openai_validation_assistant(prompt)
            if city_name != "None" and city_name != "Invalid":
                response = True
                pincode = await find_pincode_by_city_name(city_name)
            elif city_name in ["Invalid", "invalid"]:
                if language == "English":
                    return step["final_text"], "invalid_feedback"
                else:
                    prompt = f"You have to just return {step['final_text']} in translated langauage-{language} Output:as list and in same structure like the message which i have given"
                    llm_answer = await ask_openai_validation_assistant(prompt)
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
            else:
                response = False

        if response:
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            user.pincode = pincode
            await user.save()
            next_step = step["next_step"]
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            if thread:
                thread.flow_id = flow_id
                thread.step_id = next_step
                thread.previous_flow = thread.flow_id
                thread.previous_step = step["step_id"]
                await thread.save()
                user.appointment_status = AppointmentStatus.BOOKED
                await user.save()
            if language == "English":
                return step["message"], "booked"
            else:
                prompt = f"Yo have to just return {step['message']} in translated langauage-{language} Output:as valid Json translated in {language} translate the string in {language} but  do not translate the keys in dict and in same structure like the message which i have given"
                llm_answer = await ask_openai_validation_assistant(prompt)
                try:
                    llm_json = json.loads(llm_answer)
                except:
                    llm_json = [llm_answer]
                is_validated, answer = await validate_answer(
                    llm_json, step["message"], language
                )
                if is_validated:
                    return llm_json, "booked"
                else:
                    return answer, "out_of_context"
        else:
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

    prompt = f"""
You are a validation assistant.
Conversation language = {language}.
Step: {step_id}, Expecting: {step['expected_input']}
the expected input can also be in user selected language also
User input: "{user_message}"
Valid condition (regex): {step['valid_condition']}
bot_response must ALWAYS be written in {language} every string and even if it address  should be translated but fo not translate the keys of dict and the number in the string, regardless of input language or system language.



Instructions:
1. Refusal detection:
   - If the {user_message} intent states that it dosen't want to share information then return only {step['final_text']} (translated into {language}), with status = "INVALID".
   - If user input clearly expresses **refusal** (like "I don't want to give", "skip", "no", "nahi batana", "not sharing", "prefer not to say"),
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
        # fallback if model doesn't output strict JSON
        try:
            llm_json = ast.literal_eval(llm_answer)
        except:
            llm_json = {"status": "INVALID", "bot_response": step["message"]}
    is_validated, answer = await validate_answer(
        llm_json, {"status": "VALID", "bot_response": step["message"]}, language
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
        if step["step_id"] == "2":
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            if user:
                user.name = user_message
                user.appointment_status = AppointmentStatus.IN_PROCESS
                await user.save()
            else:
                user_info = User_Info(
                    name=user_message,
                    thread_id=thread_id,
                    appointment_status=AppointmentStatus.IN_PROCESS,
                )
                await user_info.insert()
        if step["step_id"] == "5":
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            user.appointment_status = AppointmentStatus.BOOKED
            await user.save()

        # Save thread
        if thread:
            thread.flow_id = flow_id
            thread.step_id = next_step
            thread.step_count = 1
            thread.previous_flow = thread.flow_id
            thread.previous_step = step["step_id"]
            await thread.save()

        if step["step_id"] == "5":
            return llm_json.get("bot_response"), "booked"
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
        if step["step_id"] in ["2", "5"] and isinstance(
            llm_json.get("bot_response"), list
        ):
            return llm_json.get("bot_response"), "invalid_feedback"
        return llm_json.get("bot_response"), None
