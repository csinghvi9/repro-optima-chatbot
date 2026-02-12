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
from app.models.otp_verification import OtpVerification
from app.core.format_check import validate_answer


async def ivfSteps(
    thread_id: str,
    flow_id: str,
    step_id: str,
    language: str,
    user_message_parameter: str,
):
    already_user = False
    steps_flow = {
        "flow_id": "ivf_steps",
        "steps": {
            "1": {
                "step_id": "1",
                "message": [
                    "To share the steps of an IVF cycle, I’ll just need a few quick details from you first",
                    "Please share your name",
                ],
                "expected_input": "User wants  to know the steps in an ivf cycle or donor oocyte cycle or donor process or processes in ivf cycle or process in donor oocyte or process in self oocyte or steps in self oocyte and this questions in any language",
                "valid_condition": "",
                "action": None,
                "other_text": "",
                "final_text": "",
                "next_step": "2",
            },
            "2": {
                "step_id": "2",
                "message": "Thanks. Please provide your mobile number",
                "expected_input": "name of the person or nick name of the person and can be any name in any language like (miqat,ekal,ellis etc) and a valid name not like abc xyz",
                "valid_condition": r"^[A-Za-z\s]{2,50}$",
                "action": "send_otp_api",
                "other_text": "Sorry, I couldn’t recognize that as a name. Could you please re-enter your full name Let's try again",  # "Please share your name it is important for appointment booking step",
                "final_text": [
                    "We cannot continue without your name. Please enter your name to proceed",
                    "You can still explore information without giving your name. Would you like to know about topics below",
                ],
                "next_step": "3",
            },
            "3": {
                "step_id": "3",
                "message": "Please enter the OTP sent to your mobile number for verification",
                "expected_input": "only ten digit phone number",
                "valid_condition": r"^\d{10}$",
                "action": "verify_otp_api",
                "other_text": "Please enter a valid ten digit Phone Number it is important for booking an appointment",
                "final_text": [
                    "We cannot continue without your phone number. Please enter your number to proceed",
                    "You can still explore information without giving your number. Would you like to know about topics below",
                ],
                "next_step": "4",
            },
            "4": {
                "step_id": "4",
                "message": [
                    "Your mobile number is verified. Thank you for confirming!",
                    "Now please mention your preferred pin code or city name",
                ],
                "expected_input": "6 digit otp",
                "valid_condition": r"^\d{6}$",
                "action": None,
                "other_text": "Oops! The OTP you entered doesn’t match. Please try again",
                "final_text": "You’ve reached the maximum OTP attempts. You can request a new OTP in 1 hour",
                "next_step": "5",
            },
            "5": {
                "step_id": "5",
                "message": [
                    "Thank you for sharing your details",
                    "A standard self- oocyte cycle comprises of following main stages",
                    {
                        "title": "Self Oocyte",
                        "steps": [
                            "Stimulation",
                            "Egg Retrieval",
                            "Sperm Collection",
                            "Insemination",
                            "Embryo Grading",
                            "Fit For Transfer",
                            "Embryo Transfer",
                            "Pregnancy Test",
                        ],
                    },
                    "However Your doctor will recommend the best IVF cycle based on your reports and history",
                    "Hope this was helpful. Let me know if you need more info",
                ],  # ,"Watch to Learn More"
                "expected_input": "pincode",
                "valid_condition": r"^\d{6}$",
                "action": "fetch_centers_api",
                "other_text": [
                    " Please enter a valid pincode or city name to check clinic availability near you",
                ],
                "final_text": [
                    "We cannot proceed with the  process without these details. Please share your pincode to continue",
                    "You can enter your city or area name instead",
                ],
                "next_step": None,
            },
        },
    }

    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)
    step_count = thread.step_count

    if thread and thread.step_id and not (user_message_parameter):
        user_message = await step_check(thread_id, steps_flow, 8)
        new_thread = await Thread.find_one(Thread.id == thread_obj_id)
        step_id = new_thread.step_id
    elif thread and thread.step_id:
        step_id = thread.step_id
        user_message = user_message_parameter
    elif not step_id:
        user_message = await step_check(thread_id, steps_flow, 5)
        new_thread = await Thread.find_one(Thread.id == thread_obj_id)
        if new_thread.step_id:
            step_id = new_thread.step_id
            prompt1 = f"You are a strict keyword-based classifier. If the user message contains any of the exact phrases “donor oocyte”, “donor egg”, “egg donor”, or “donor IVF” in any language, output donor. Do not interpret intent or meaning and do not infer anything beyond exact keyword presence. Only check for the explicit presence of these donor-related terms. If none of these phrases appear in the message, output self. Respond with only one word: donor or self. user_message={user_message_parameter}"
            preffered_ivf_step = await ask_openai_validation_assistant(prompt1)
            user_info = await User_Info.find_one(User_Info.thread_id == thread_id)
            user_info.preffered_ivf_step = preffered_ivf_step
            await user_info.save()
            if step_id == "5":
                steps_flow["steps"]["5"]["message"].pop(0)
                # prompt1=f"You are a strict keyword-based classifier. If the user message contains any of the exact phrases “donor oocyte”, “donor egg”, “egg donor”, or “donor IVF” in any language, output donor. Do not interpret intent or meaning and do not infer anything beyond exact keyword presence. Only check for the explicit presence of these donor-related terms. If none of these phrases appear in the message, output self. Respond with only one word: donor or self. user_message={user_message_parameter}"
                # preffered_ivf_step = await ask_openai_validation_assistant(prompt1)
                # print("the preffered_ivf_step is ",preffered_ivf_step)
                # user_info = await  User_Info.find_one(User_Info.thread_id == thread_id)
                # user_info.preffered_ivf_step=preffered_ivf_step
                # await user_info.save()
                already_user = True

        else:
            step_id = "1"
            user_message = user_message_parameter

    # steps_flow = {
    #     "flow_id": "ivf_steps",
    #     "steps": {
    #         "1": {
    #             "step_id": "1",
    #             "message": ["To share the steps of an IVF cycle, I’ll just need a few quick details from you first","Please share your name"],
    #             "expected_input": "User wants  to know the steps in an ivf cycle or What are the steps in an IVF cycle",
    #             "valid_condition": "",
    #             "action": None,
    #             "other_text": "",
    #             "final_text": "",
    #             "next_step": "2",
    #         },
    #         "2": {
    #             "step_id": "2",
    #             "message": "Thanks. Please provide your mobile number",
    #             "expected_input": "name of the person",
    #             "valid_condition": r"^[A-Za-z\s]{2,50}$",
    #             "action": "send_otp_api",
    #             "other_text": "Sorry, I couldn’t recognize that as a name. Could you please re-enter your full name Let's try again",  # "Please share your name it is important for appointment booking step",
    #             "final_text": [
    #                 "We cannot continue with the booking without your name. Please enter your name to proceed",
    #                 "You can still explore information without giving your name. Would you like to know about topics below",
    #             ],
    #             "next_step": "3",
    #         },
    #         "3": {
    #             "step_id": "3",
    #             "message": "Please enter the OTP sent to your mobile number for verification",
    #             "expected_input": "only ten digit phone number",
    #             "valid_condition": r"^\d{10}$",
    #             "action": "verify_otp_api",
    #             "other_text": "Please enter a valid ten digit Phone Number it is important for booking an appointment",
    #             "final_text": [
    #                 "We cannot continue with the booking without your phone number. Please enter your number to proceed",
    #                 "You can still explore information without giving your number. Would you like to know about topics below",
    #             ],
    #             "next_step": "4",
    #         },
    #         "4": {
    #             "step_id": "4",
    #             "message": [
    #                 "Your mobile number is verified. Thank you for confirming!",
    #                 "Now please mention your preferred pin code",
    #             ],
    #             "expected_input": "6 digit otp",
    #             "valid_condition": r"^\d{6}$",
    #             "action": None,
    #             "other_text": "Oops! The OTP you entered doesn’t match. Please try again",
    #             "final_text": "You’ve reached the maximum OTP attempts. You can request a new OTP in 1 hour",
    #             "next_step": "5",
    #         },
    #         "5": {
    #             "step_id": "5",
    #             "message": ["Thank you for sharing your details","A standard self- oocyte cycle comprises of following main stages",{"title":"Self Oocyte","steps":['Stimulation','Egg Retrieval','Sperm Collection','Embryo Grading','Fit For Transfer','Embryo Transfer','Pregnancy Test']},"However Your doctor will recommend the best IVF cycle based on your reports and history"],
    #             "expected_input": "pincode",
    #             "valid_condition": r"^\d{6}$",
    #             "action": "fetch_centers_api",
    #             "other_text": [
    #                 "Sorry, the Pincode is invalid",
    #                 " Please enter a valid pincode to check clinic availability near you",
    #             ],
    #             "final_text": [
    #                 "We cannot proceed with the booking process without these details. Please share your pincode to continue",
    #                 "You can enter your city or area name instead",
    #             ],
    #             "next_step": None,
    #         },
    #     },
    # }

    step = steps_flow["steps"].get(step_id)
    if not step:
        return {"error": "Invalid step"}

    if not user_message or user_message.strip() == "":
        user_message = ""

    existing_user = await User_Info.find_one(User_Info.thread_id == thread_id)
    if step["step_id"] == "3":
        match = re.search(r"\b\d{10}\b", user_message)
        if match:
            phone_number = match.group(0)
            # the actual 10-digit number
            if existing_user.name:
                otp_request = OtpRequest(
                    contact_no=phone_number, name=existing_user.name
                )
            else:
                otp_request = OtpRequest(contact_no=phone_number, name="Guest")
            otp = await create_or_update_otp_entry(otp_request, thread_id)
            if "Try later" in otp.get("message", ""):
                if language == "English":
                    return (
                        "You have reached the maximum number of resend attempts. Please try again later",
                        "change_phone_number",
                    )
                else:
                    prompt = f"Translate the following text 'You have reached the maximum number of resend attempts. Please try again later' into {language} and return only the translated text with no additions or explanations: OUTPUT_FORMAT:string"
                    llm_answer = await ask_openai_validation_assistant(prompt)
                    try:
                        llm_json = json.loads(llm_answer)
                    except:
                        llm_json = [llm_answer]
                    is_validated, answer = await validate_answer(
                        llm_json,
                        "You have reached the maximum number of resend attempts. Please try again later",
                        language,
                    )
                    if is_validated:
                        return llm_json, "change_phone_number"
                    else:
                        return answer, "out_of_context"
            elif otp.get("otp_code"):
                await send_indira_otp(contact_no=phone_number, otp_code=otp["otp_code"])
                otp.pop("otp_code", None)
                thread.flow_id = flow_id
                thread.step_id = step["next_step"]
                thread.step_count = 1
                thread.previous_flow = thread.flow_id
                thread.previous_step = step["step_id"]
                await thread.save()
                user = await User_Info.find_one(User_Info.thread_id == thread_id)
                user.phone_number = phone_number
                await user.save()
                if language == "English" and thread:
                    return step["message"], "resend_otp"
                else:
                    prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['message']} OUTPUT_FORMAT:string"
                    llm_answer = await ask_openai_validation_assistant(prompt)
                    is_validated, answer = await validate_answer(
                        llm_answer, step["message"], language
                    )
                    if is_validated:
                        return llm_answer, "resend_otp"
                    else:
                        return answer, "out_of_context"
        else:
            prompt = f"""
                    You are a classification assistant.

                    User message: "{user_message}"

                    You must classify the input into one of these categories:

                    1. **refusal** — The user *explicitly or implicitly* refuses to share contact information, e.g. messages like:
                    - "I don't want to share"
                    - "prefer not to give"
                    - "no number"
                    - "skip this"
                    - "not comfortable"
                    - "won’t provide"
                    - (any linguistic equivalent in {language})

                    2. **invalid** — The user message is *not a valid phone number* according to expected format: {step['expected_input']}
                    and valid conditions: {step['valid_condition']}.
                    Invalid means: 
                    - it contains letters (e.g. 12121212ab)
                    - it’s too short or too long
                    - it includes special symbols other than + or digits
                    - it’s a random or malformed entry, but still an attempt to provide a number

                    ⚠️ Important:
                    - If the message looks like an attempt to enter a phone number but fails format validation → classify as **invalid**, *not* refusal.
                    - Only classify as **refusal** if user explicitly says they don’t want to share or declines to provide the number.

                    ---

                    If classification = refusal:
                    Translate the following text into {language} and return only the translated text (as a list of 2 strings):
                    {step['final_text']}

                    If classification = invalid:
                    Translate the following text into {language} and return only the translated text:
                    {step['other_text']}

                    OUTPUT_FORMAT:
                    {{
                    "classification": "refusal" or "invalid",
                    "translated_text": [ ... ]
                    }}
                    """

            llm_answer = await ask_openai_validation_assistant(prompt)
            try:
                llm_answer = json.loads(llm_answer)  # will give list
            except:
                try:
                    llm_answer = ast.literal_eval(llm_answer)
                except Exception:
                    llm_answer = [llm_answer]
            if llm_answer.get("classification") == "refusal":
                is_validated, answer = await validate_answer(
                    llm_answer,
                    {
                        "classification": "refusal",
                        "translated_text": [
                            "We cannot continue without your phone number. Please enter your number to proceed",
                            "You can still explore information without giving your number. Would you like to know about topics below",
                        ],
                    },
                    language,
                )
                if is_validated:
                    return llm_answer.get("translated_text"), "invalid_feedback"
                else:
                    return answer, "out_of_context"
            else:
                is_validated, answer = await validate_answer(
                    llm_answer,
                    {
                        "classification": "refusal",
                        "translated_text": [
                            "Please enter a valid ten digit Phone Number it is important for booking an appointment"
                        ],
                    },
                    language,
                )
                if is_validated:
                    return llm_answer.get("translated_text"), "change_phone_number"
                else:
                    return answer, "out_of_context"
        # if not(match) and language=="English":
        #     return step["other_text"], None

    if step["step_id"] == "4":
        match = re.search(r"\b\d{6}\b", user_message)
        if match:
            otp = match.group(0)
            otp_request = OtpVerify(
                otp_code=otp,
                contact_no=existing_user.phone_number,
                name=existing_user.name,
            )
            result = await verify_otp_entry(otp_request, thread_id)
            if isinstance(result, dict):
                if "OTP expired" in result.get("message", ""):
                    if existing_user.name:
                        otp_request = OtpRequest(
                            contact_no=existing_user.phone_number,
                            name=existing_user.name,
                        )
                    else:
                        otp_request = OtpRequest(
                            contact_no=existing_user.phone_number, name="Guest"
                        )
                    otp = await create_or_update_otp_entry(otp_request, thread_id)
                    await send_indira_otp(
                        contact_no=existing_user.phone_number, otp_code=otp["otp_code"]
                    )
                    if language == "English":
                        return (
                            "Your Otp is Expired please enter the New OTP send on you Registered Mobile Number",
                            "resend_otp",
                        )
                    else:
                        prompt = f"Translate the following text 'Your Otp is Expired please enter the New OTP send on your Registered Mobile Number' into {language} and return only the translated text with no additions or explanations: OUTPUT_FORMAT:string"
                        llm_answer = await ask_openai_validation_assistant(prompt)
                        try:
                            llm_json = json.loads(llm_answer)
                        except:
                            llm_json = [llm_answer]
                        is_validated, answer = await validate_answer(
                            llm_json,
                            "Your Otp is Expired please enter the New OTP send on your Registered Mobile Number",
                            language,
                        )
                        if is_validated:
                            return llm_json, "resend_otp"
                        else:
                            return answer, "out_of_context"
            if result and language == "English" and thread:
                thread.flow_id = flow_id
                thread.step_id = step["next_step"]
                thread.step_count = 1
                thread.previous_flow = thread.flow_id
                thread.previous_step = step["step_id"]
                await thread.save()
                return step["message"], None
            if result and language != "English":
                thread.flow_id = flow_id
                thread.step_id = step["next_step"]
                thread.step_count = 1
                thread.previous_flow = thread.flow_id
                thread.previous_step = step["step_id"]
                await thread.save()
                prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations and in double quotes:\n{step['message']} OUTPUT_FORMAT:list"
                llm_answer = await ask_openai_validation_assistant(prompt)
                try:
                    llm_json = ast.literal_eval(llm_answer)
                except Exception as e:
                    llm_json = [llm_answer]
                is_validated, answer = await validate_answer(
                    llm_json, step["message"], language
                )
                if is_validated:
                    return llm_json, None
                else:
                    return answer, "out_of_context"
            if not (result) and language == "English":
                otp = await OtpVerification.find_one(
                    OtpVerification.thread_id == thread_id
                )
                if otp and otp.resend_attempts >= otp.max_resend_attempts:
                    return step["final_text"], "change_phone_number"
                elif otp and otp.otp_code:
                    return step["other_text"], "resend_otp"
                else:
                    if existing_user.name:
                        otp_request = OtpRequest(
                            contact_no=existing_user.phone_number,
                            name=existing_user.name,
                        )
                    else:
                        otp_request = OtpRequest(
                            contact_no=existing_user.phone_number, name="Guest"
                        )
                    otp = await create_or_update_otp_entry(otp_request, thread_id)
                    if otp.get("otp_code"):
                        await send_indira_otp(
                            contact_no=existing_user.phone_number,
                            otp_code=otp["otp_code"],
                        )
                        return step["other_text"], "resend_otp"
                    if "Maximum attempts reached" in otp.get("message", ""):
                        return step["final_text"], "change_phone_number"
            if not (result) and language != "English":
                otp = await OtpVerification.find_one(
                    OtpVerification.thread_id == thread_id
                )
                frommax = False
                if otp and otp.resend_attempts >= otp.max_resend_attempts:
                    frommax = True
                    prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['final_text']} OUTPUT_FORMAT:string"
                    llm_answer = await ask_openai_validation_assistant(prompt)
                elif otp and otp.otp_code:
                    # await send_indira_otp(contact_no=existing_user.phone_number, otp_code=otp["otp_code"])
                    prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['other_text']} OUTPUT_FORMAT:string"
                    llm_answer = await ask_openai_validation_assistant(prompt)
                    if existing_user.name:
                        otp_request = OtpRequest(
                            contact_no=existing_user.phone_number,
                            name=existing_user.name,
                        )
                    else:
                        otp_request = OtpRequest(
                            contact_no=existing_user.phone_number, name="Guest"
                        )
                else:
                    otp = await create_or_update_otp_entry(otp_request, thread_id)
                    frommax = False
                    if otp.get("otp_code"):
                        await send_indira_otp(
                            contact_no=existing_user.phone_number,
                            otp_code=otp["otp_code"],
                        )
                        prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['other_text']} OUTPUT_FORMAT:string"
                        llm_answer = await ask_openai_validation_assistant(prompt)
                        if existing_user.name:
                            otp_request = OtpRequest(
                                contact_no=existing_user.phone_number,
                                name=existing_user.name,
                            )
                        else:
                            otp_request = OtpRequest(
                                contact_no=existing_user.phone_number, name="Guest"
                            )
                    if "Maximum attempts reached" in otp.get("message", ""):
                        frommax = True
                        prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['final_text']} OUTPUT_FORMAT:string"
                        llm_answer = await ask_openai_validation_assistant(prompt)
                try:
                    llm_json = json.loads(llm_answer)
                except:
                    llm_json = [llm_answer]
                if not (frommax):
                    is_validated, answer = await validate_answer(
                        llm_json, step["other_text"], language
                    )
                    if is_validated:
                        return llm_json, "resend_otp"
                    else:
                        return answer, "out_of_context"
                else:
                    is_validated, answer = await validate_answer(
                        llm_json, step["final_text"], language
                    )
                    if is_validated:
                        return llm_json, "change_phone_number"
                    else:
                        return answer, "out_of_context"
        else:
            otp_match = re.search(r"\b\d+\b", user_message)
            if otp_match:
                otp = otp_match.group(0)
            else:
                otp = None
            if otp:
                otp_request = OtpVerify(
                    otp_code=otp,
                    contact_no=existing_user.phone_number,
                    name=existing_user.name,
                )
                result = await verify_otp_entry(otp_request, thread_id)
                if isinstance(result, dict):
                    if "OTP expired" in result.get("message", ""):
                        if existing_user.name:
                            otp_request = OtpRequest(
                                contact_no=existing_user.phone_number,
                                name=existing_user.name,
                            )
                        else:
                            otp_request = OtpRequest(
                                contact_no=existing_user.phone_number, name="Guest"
                            )
                        otp = await create_or_update_otp_entry(otp_request, thread_id)
                        await send_indira_otp(
                            contact_no=existing_user.phone_number,
                            otp_code=otp["otp_code"],
                        )
                        if language == "English":
                            return (
                                "Your Otp is Expired please enter the New OTP send on your Registered Mobile Number",
                                "resend_otp",
                            )
                        else:
                            prompt = f"Translate the following text 'Your Otp is Expired please enter the New OTP send on your Registered Mobile Number' into {language} and return only the translated text with no additions or explanations: OUTPUT_FORMAT:string"
                            llm_answer = await ask_openai_validation_assistant(prompt)
                            try:
                                llm_json = json.loads(llm_answer)
                            except:
                                llm_json = [llm_answer]
                            is_validated, answer = await validate_answer(
                                llm_json,
                                "Your Otp is Expired please enter the New OTP send on your Registered Mobile Number",
                                language,
                            )
                            if is_validated:
                                return llm_json, "resend_otp"
                            else:
                                return answer, "out_of_context"
                elif language == "English":
                    otp = await OtpVerification.find_one(
                        OtpVerification.thread_id == thread_id
                    )
                    if otp and otp.resend_attempts >= otp.max_resend_attempts:
                        return step["final_text"], "change_phone_number"
                    elif otp and otp.otp_code:
                        return step["other_text"], "resend_otp"
                    else:
                        if existing_user.name:
                            otp_request = OtpRequest(
                                contact_no=existing_user.phone_number,
                                name=existing_user.name,
                            )
                        else:
                            otp_request = OtpRequest(
                                contact_no=existing_user.phone_number, name="Guest"
                            )
                        otp = await create_or_update_otp_entry(otp_request, thread_id)
                        if otp.get("otp_code"):
                            await send_indira_otp(
                                contact_no=existing_user.phone_number,
                                otp_code=otp["otp_code"],
                            )
                            return step["other_text"], "resend_otp"
                        if "Maximum attempts reached" in otp.get("message", ""):
                            return step["final_text"], "change_phone_number"
                else:
                    otp = await OtpVerification.find_one(
                        OtpVerification.thread_id == thread_id
                    )
                    frommax = False
                    if otp and otp.resend_attempts >= otp.max_resend_attempts:
                        frommax = True
                        prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['final_text']} OUTPUT_FORMAT:string"
                        llm_answer = await ask_openai_validation_assistant(prompt)
                    elif otp and otp.otp_code:
                        prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['other_text']} OUTPUT_FORMAT:string"
                        llm_answer = await ask_openai_validation_assistant(prompt)
                    else:
                        otp = await create_or_update_otp_entry(otp_request, thread_id)
                        frommax = False
                        if otp.get("otp_code"):
                            await send_indira_otp(
                                contact_no=existing_user.phone_number,
                                otp_code=otp["otp_code"],
                            )
                            prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['other_text']} OUTPUT_FORMAT:string"
                            llm_answer = await ask_openai_validation_assistant(prompt)
                            if existing_user.name:
                                otp_request = OtpRequest(
                                    contact_no=existing_user.phone_number,
                                    name=existing_user.name,
                                )
                            else:
                                otp_request = OtpRequest(
                                    contact_no=existing_user.phone_number, name="Guest"
                                )
                        if "Maximum attempts reached" in otp.get("message", ""):
                            frommax = True
                            prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['final_text']} OUTPUT_FORMAT:string"
                            llm_answer = await ask_openai_validation_assistant(prompt)
                    try:
                        llm_json = json.loads(llm_answer)
                    except:
                        llm_json = [llm_answer]
                    if not (frommax):
                        is_validated, answer = await validate_answer(
                            llm_json, step["other_text"], language
                        )
                        if is_validated:
                            return llm_json, "resend_otp"
                        else:
                            return answer, "out_of_context"
                    else:
                        is_validated, answer = await validate_answer(
                            llm_json, step["final_text"], language
                        )
                        if is_validated:
                            return llm_json, "change_phone_number"
                        else:
                            return answer, "out_of_context"
            else:
                if language == "English":
                    otp = await OtpVerification.find_one(
                        OtpVerification.thread_id == thread_id
                    )
                    if otp and otp.resend_attempts >= otp.max_resend_attempts:
                        return step["final_text"], "change_phone_number"
                    elif otp and otp.otp_code:
                        return step["other_text"], "resend_otp"
                    else:
                        if existing_user.name:
                            otp_request = OtpRequest(
                                contact_no=existing_user.phone_number,
                                name=existing_user.name,
                            )
                        else:
                            otp_request = OtpRequest(
                                contact_no=existing_user.phone_number, name="Guest"
                            )
                        otp = await create_or_update_otp_entry(otp_request, thread_id)
                        if otp.get("otp_code"):
                            await send_indira_otp(
                                contact_no=existing_user.phone_number,
                                otp_code=otp["otp_code"],
                            )
                            return step["other_text"], "resend_otp"
                        if "Maximum attempts reached" in otp.get("message", ""):
                            return step["final_text"], "change_phone_number"
                else:
                    otp = await OtpVerification.find_one(
                        OtpVerification.thread_id == thread_id
                    )
                    frommax = False
                    if otp and otp.resend_attempts >= otp.max_resend_attempts:
                        frommax = True
                        prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['final_text']} OUTPUT_FORMAT:string"
                        llm_answer = await ask_openai_validation_assistant(prompt)
                    elif otp and otp.otp_code:
                        prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['other_text']} OUTPUT_FORMAT:string"
                        llm_answer = await ask_openai_validation_assistant(prompt)
                    else:
                        frommax = False
                        if existing_user.name:
                            otp_request = OtpRequest(
                                contact_no=existing_user.phone_number,
                                name=existing_user.name,
                            )
                        else:
                            otp_request = OtpRequest(
                                contact_no=existing_user.phone_number, name="Guest"
                            )
                        otp = await create_or_update_otp_entry(otp_request, thread_id)
                        if otp.get("otp_code"):
                            await send_indira_otp(
                                contact_no=existing_user.phone_number,
                                otp_code=otp["otp_code"],
                            )
                            prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['other_text']} OUTPUT_FORMAT:string"
                            llm_answer = await ask_openai_validation_assistant(prompt)
                            if existing_user.name:
                                otp_request = OtpRequest(
                                    contact_no=existing_user.phone_number,
                                    name=existing_user.name,
                                )
                            else:
                                otp_request = OtpRequest(
                                    contact_no=existing_user.phone_number, name="Guest"
                                )
                        if "Maximum attempts reached" in otp.get("message", ""):
                            frommax = True
                            prompt = f"Translate the following text into {language} and return only the translated text with no additions or explanations:\n{step['final_text']} OUTPUT_FORMAT:string"
                            llm_answer = await ask_openai_validation_assistant(prompt)

                    # otp = await create_or_update_otp_entry(otp_request, thread_id)
                    # await send_indira_otp(contact_no=existing_user.phone_number, otp_code=otp["otp_code"])
                    try:
                        llm_json = json.loads(llm_answer)
                    except:
                        llm_json = [llm_answer]
                    if not (frommax):
                        is_validated, answer = await validate_answer(
                            llm_json, step["other_text"], language
                        )
                        if is_validated:
                            return llm_json, "resend_otp"
                        else:
                            return answer, "out_of_context"
                    else:
                        is_validated, answer = await validate_answer(
                            llm_json, step["final_text"], language
                        )
                        if is_validated:
                            return llm_json, "change_phone_number"
                        else:
                            return answer, "out_of_context"

        # if not(match) and language=="English":
        #     return step["other_text"], None

    if step["step_id"] == "5":
        match = re.search(r"\b\d{6}\b", user_message)
        if match:
            pincode = match.group(0)  # the actual 6-digit code
            response = True  # await find_nearest_by_postal(pincode,"pincode")
        # pass only the pincode
        # elif len(user_message) == 1 and language=="English":
        #         response =True # await find_nearest_by_postal(user_message, "city")
        #         pincode = await find_pincode_by_city_name(user_message)

        else:
            prompt = f"Your work is to give the city name from this text:{user_message} if it is in another language other than english then convert city name in english and if there is no city name then return None and If the user refuses to give location information (for example: 'I don’t want to share', 'not sure', 'skip', 'no', 'none'), return Invalid. don't give any text from your own only None,Cityname"
            city_name = await ask_openai_validation_assistant(prompt)
            if city_name != "None" and city_name != "Invalid":
                response = True  # await find_nearest_by_postal(city_name, "city")
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
            # user.preffered_center = response
            user.pincode = pincode
            await user.save()
            next_step = step["next_step"]
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            if not user.crm_api_send:
                result = await call_ivf_lead_creation_api(
                    full_name=user.name,
                    contact_no=user.phone_number,
                    pincode=user.pincode,
                )
                user.crm_api_send = True
                await user.save()
            if thread:
                thread.flow_id = flow_id
                thread.step_id = next_step
                thread.previous_flow = thread.flow_id
                thread.previous_step = step["step_id"]
                await thread.save()
            user_info = await User_Info.find_one(User_Info.thread_id == thread_id)
            if user_info:
                if user_info.preffered_ivf_step.lower() == "donor" and not (
                    already_user
                ):
                    step["message"][
                        1
                    ] = "A standard donor oocyte cycle comprises of following main stages"
                    step["message"][2] = {
                        "title": "Donor Oocyte",
                        "steps": [
                            "Sperm Collection",
                            "Insemination",
                            "Embryo Grading",
                            "Fit For Transfer",
                            "Embryo Transfer",
                            "Pregnancy Test",
                        ],
                    }
                elif user_info.preffered_ivf_step.lower() == "donor" and already_user:
                    step["message"][
                        0
                    ] = "A standard donor oocyte cycle comprises of following main stages"
                    step["message"][1] = {
                        "title": "Donor Oocyte",
                        "steps": [
                            "Sperm Collection",
                            "Insemination",
                            "Embryo Grading",
                            "Fit For Transfer",
                            "Embryo Transfer",
                            "Pregnancy Test",
                        ],
                    }

            if language == "English":
                return step["message"], "ivf_steps"
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
        # else:
        # return ["Sorry, the Pincode is invalid"," Please enter a valid pincode to check clinic availability near you"], None
    prompt = f"""
You are a validation assistant.
Conversation language = {language}.
Step: {step_id}, Expecting: {step['expected_input']}
the expected input can also be in user selected language and can be in any langugae you just have to validate by understanding the question also 
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
   - If the input matches {step['valid_condition']} or {step['expected_input']} (regex + meaning check), 
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

    # client = boto3.client("bedrock-runtime")
    # model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    # response = client.converse(
    #     modelId=model_id,
    #     messages=[{"role": "user", "content": [{"text": prompt}]}],
    #     inferenceConfig={"maxTokens": 500, "temperature": 0},
    # )

    # llm_answer = response["output"]["message"]["content"][0]["text"].strip()

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
        if step["step_id"] == "1":
            prompt1 = f"You are a strict keyword-based classifier. If the user message contains any of the exact phrases “donor oocyte”, “donor egg”, “egg donor”, or “donor IVF” in any language, output donor. Do not interpret intent or meaning and do not infer anything beyond exact keyword presence. Only check for the explicit presence of these donor-related terms. If none of these phrases appear in the message, output self. Respond with only one word: donor or self. user_message={user_message}"
            preffered_ivf_step = await ask_openai_validation_assistant(prompt1)
            user_info = await User_Info.find_one(User_Info.thread_id == thread_id)
            if user_info:
                user_info.preffered_ivf_step = preffered_ivf_step
                await user_info.save()
            else:
                user_info = User_Info(
                    preffered_ivf_step=preffered_ivf_step, thread_id=thread_id
                )
                await user_info.insert()
        if step["step_id"] == "2":
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            if user:
                user.name = user_message
                await user.save()
            else:
                user_info = User_Info(name=user_message, thread_id=thread_id)
                await user_info.insert()
        if step["step_id"] == "3":
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            user.phone_number = user_message
            await user.save()
        if step["step_id"] == "5":
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            user.pincode = user_message
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
            return llm_json.get("bot_response"), "ivf_steps"
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
        if step["step_id"] in ["2", "3", "5"] and isinstance(
            llm_json.get("bot_response"), list
        ):
            return llm_json.get("bot_response"), "invalid_feedback"
        return llm_json.get("bot_response"), None
