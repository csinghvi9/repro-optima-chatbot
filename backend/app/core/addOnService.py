from app.utils.llm_utils import ask_openai_validation_assistant
from app.models.threads import Thread
from app.models.user_info import User_Info
from app.core.ivf_centers import find_pincode_by_city_name
from app.core.findHospital import CLINIC_CENTER
from bson import ObjectId
import json
import re
from app.core.existingUser import step_check

import ast
from app.models.user_info import User_Info
from app.core.format_check import validate_answer


async def AddONServices(
    thread_id: str, flow_id: str, step_id: str, language: str, user_message: str
):
    already_details_given = False
    user_original_message = user_message
    services_flow = {
        "flow_id": "add_on_service",
        "steps": {
            "1": {
                "step_id": "1",
                "message": ["To share details about the Test, please share your name"],
                "expected_input": "The user wants to know services or different medical test information provided by the ivf.",
                "valid_condition": "",
                "action": None,
                "other_text": [
                    "Currently I don't have information about this test",
                    {
                        "first_text": "For more specific information, please connect with our call center between 9 AM and 6 PM.",
                        "second_text": "CUSTOMER CARE NUMBER",
                        "phone_number": "+6332-256-2433",
                    },
                    "Hope this helps! You can come back anytime to explore  or get more info",
                ],
                "final_text": "",
                "next_step": "2",
            },
            "2": {
                "step_id": "2",
                "message": [
                    "Thank you! Now please share your phone number so we can assist you better",
                ],
                "expected_input": "name of the person or nick name of the person and can be any name in any language like (miqat,ekal,ellis etc) and a valid name not like abc xyz",
                "valid_condition": r"^[A-Za-z\s]{2,50}$",
                "action": None,
                "other_text": "Sorry, I couldn't recognize that as a name. Could you please re-enter your full name Let's try again",
                "final_text": [
                    "We cannot continue without your name. Please enter your name to proceed",
                    "You can still explore information without giving your name. Would you like to know about topics below",
                ],
                "next_step": "3",
            },
            "3": {
                "step_id": "3",
                "message": [
                    "Thank you for sharing your details",
                    "To understand more about these, search for them in the query box below",
                ],
                "expected_input": "phone number or mobile number of the user (10-13 digits, may start with + or 0)",
                "valid_condition": r"^[\+]?[\d\-\s]{10,13}$",
                "action": None,
                "other_text": "Sorry, that doesn't look like a valid phone number. Please enter your phone number. It should contain 10–13 digits.",
                "final_text": [
                    "We cannot continue without your phone number. Please enter your phone number. It should contain 10–13 digits. to proceed",
                    "You can still explore information without giving your phone number. Would you like to know about topics below",
                ],
                "next_step": "5",
            },
            "5": {
                "step_id": "5",
                "message": [
                    "Thank you for sharing your details",
                    "To understand more about these, search for them in the query box below",
                ],
                "expected_input": "pincode",
                "valid_condition": r"^\d{6}$",
                "action": "fetch_centers_api",
                "other_text": [
                    " Please enter a valid pincode or city name  to check clinic availability near you"
                ],
                "final_text": [
                    "We cannot proceed with the Service process without these details. Please share your pincode to continue",
                    "You can enter your city or area name instead",
                ],
                "next_step": None,
            },
        },
    }
    allowed_add_on_services = [
        "Services:",
        "1. Fertility Screening and Investigation",
        "2. Ovulation Induction and Monitoring",
        "3. Intrauterine Insemination (IUI)",
        "4. In-vitro Fertilization (IVF)",
        "5. Treatment of Male Infertility / Assisted Fertilization (ICSI)",
        "6. Gamete Intra-Fallopian Transfer (GIFT), Zygote Intra-Fallopian Transfer (ZIFT) and Tubal Embryo Transfers (TET)",
        "7. Surgical Sperm Retrieval (MESA, TESE)",
        "8. Assisted Hatching",
        "9. Embryo Freezing and Replacement of Frozen Embryos",
        "10. Sperm, Oocyte and Embryo Banking",
        "11. Infertility Surgery: Gynecologic Laparoscopy and Hysteroscopy",
    ]
    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)
    step_count = thread.step_count
    print(f"[ADD_ON_SERVICE] Entry: flow_id={flow_id}, step_id={step_id}, thread.step_id={thread.step_id}, user_message={user_message[:50] if user_message else None}")
    if thread and thread.step_id and not (user_message):
        print(f"[ADD_ON_SERVICE] Branch: thread.step_id exists, no user_message → step_check")
        user_message = await step_check(thread_id, services_flow, 8)
        new_thread = await Thread.find_one(Thread.id == thread_obj_id)
        step_id = new_thread.step_id
        print(f"[ADD_ON_SERVICE] After step_check: step_id={step_id}, user_message={user_message[:50] if user_message else None}")
    elif thread and thread.step_id:
        step_id = thread.step_id
        print(f"[ADD_ON_SERVICE] Branch: thread.step_id exists, has user_message → step_id={step_id}")
    elif not step_id:
        print(f"[ADD_ON_SERVICE] Branch: no step_id → step_check for existing user")
        user_message = await step_check(thread_id, services_flow, 5)
        new_thread = await Thread.find_one(Thread.id == thread_obj_id)
        print(f"[ADD_ON_SERVICE] After step_check(no_step): new_thread.step_id={new_thread.step_id}, user_message={user_message[:50] if user_message else None}")
        if new_thread.step_id:
            step_id = new_thread.step_id
            prompt = f"""
                    Extract the medical test name from this message: "{user_original_message}".
                    The test name can also be in a different language.
                    Return only the test name as a string.

                    Rules:
                    1. ***IMP**-If the user directly mentions a test name or service name and it exists in this list {allowed_add_on_services}, return that exact test name only.
                    2. If the user mentions a serial number (integer):
                    - Match the serial number exactly with the index/ID in {allowed_add_on_services}.
                    - Do NOT partially match numbers. For example: "20" MUST NOT match "2" or "0".
                    - If the serial number exists → return the corresponding test name only.
                    - If the serial number does not exist → return "None".
                    3. If the user provides a test name that is not present in {allowed_add_on_services}, return "None".
                    4. If the message is general and does not reference any specific test or number, return "None".

                    Output format: Only return one of:
                    - the exact test name
                    - "None"

                    """
            llm_answer = await ask_openai_validation_assistant(prompt, max_tokens=50)
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            h = user.preffered__medical_test
            user.preffered__medical_test = llm_answer
            await user.save()
            if step_id == "5":
                services_flow["steps"]["5"]["message"].pop(0)
                already_details_given = True
                # prompt = f"""
                #     Extract the medical test name from this message: "{user_original_message}".
                #     The test name can also be in a different language.
                #     Return only the test name as a string.

                #     Rules:
                #     1. If the user directly mentions a test name and it exists in this list {allowed_add_on_services}, return that exact test name only.
                #     2. If the user mentions a serial number (integer):
                #     - Match the serial number exactly with the index/ID in {allowed_add_on_services}.
                #     - Do NOT partially match numbers. For example: "20" MUST NOT match "2" or "0".
                #     - If the serial number exists → return the corresponding test name only.
                #     - If the serial number does not exist → return "None".
                #     3. If the user provides a test name that is not present in {allowed_add_on_services}, return "None".
                #     4. If the message is general and does not reference any specific test or number, return "None".

                #     Output format: Only return one of:
                #     - the exact test name
                #     - "None"

                #     """
                # llm_answer = await ask_openai_validation_assistant(prompt,max_tokens=50)
                # user=await User_Info.find_one(User_Info.thread_id == thread_id)
                # h=user.preffered__medical_test
                # user.preffered__medical_test=llm_answer
                # print("the test provided by llm is ",llm_answer,h)
                # await user.save()

        else:
            step_id = "1"
            user_message = user_original_message

    step = services_flow["steps"].get(step_id)
    print(f"[ADD_ON_SERVICE] Resolved: step_id={step_id}, step_exists={step is not None}")
    if not step:
        return {"error": "Invalid step"}

    if not user_message or user_message.strip() == "":
        user_message = ""

    existing_user = await User_Info.find_one(User_Info.thread_id == thread_id)
    # if user_message and step_id=="1":
    #     print("in if condition")
    #     prompt=f"extract the medical test that the user wants to get from {user_message} only give test name no description about test or anything only test name output:string and if there is not test specified then return None and if user wants to know different type of test then also return None and "
    #     llm_answer = await ask_openai_validation_assistant(prompt,max_tokens=50)
    #     user=User_Info(
    #         preffered__medical_test=llm_answer,
    #         thread_id=thread_id
    #     )
    #     await user.insert()
    #     print("the user is ",user)
    #     print("the test name is ",llm_answer)

    if step["step_id"] == "5":
        # Skip pincode - directly show services using hardcoded clinic
        user = await User_Info.find_one(User_Info.thread_id == thread_id)
        if user:
            user.preffered_center = [CLINIC_CENTER]
            await user.save()

        if thread:
            thread.flow_id = flow_id
            thread.step_id = None
            thread.previous_flow = thread.flow_id
            thread.previous_step = step["step_id"]
            await thread.save()

        step_msg = list(step["message"])  # copy

        # Translate static text messages for non-English languages
        if language != "English":
            for i, item in enumerate(step_msg):
                if isinstance(item, str) and item.strip():
                    translated = await ask_openai_validation_assistant(
                        f"Translate this sentence to {language}, output only the translated sentence: '{item}' output-string", max_tokens=100
                    )
                    if isinstance(translated, str) and translated.strip().lower() != "none":
                        step_msg[i] = translated

        if user and user.preffered__medical_test and user.preffered__medical_test not in [
            "None",
            "none",
        ]:
            prompt = f"give a brief explaination about this test : {user.preffered__medical_test} in 10-20 wored in this language:{language} output-format:-string"
            llm_answer = await ask_openai_validation_assistant(
                prompt, max_tokens=200
            )
            if already_details_given:
                step_msg.insert(0, llm_answer)
            else:
                step_msg.insert(1, llm_answer)
        else:
            services_list = list(allowed_add_on_services)
            heading = "Repro IVF offers a variety of services and advanced tests to support fertility, pregnancy, and reproductive health. Here are some of the key ones:"
            if language == "English":
                # No LLM needed for English - use the list directly
                services_answer = "\n".join(services_list)
            else:
                # Translate heading body (without brand name) and services list
                heading_prompt = f"Translate this sentence to {language}, output only the translated sentence: 'offers a variety of services and advanced tests to support fertility, pregnancy, and reproductive health. Here are some of the key ones:' output-string"
                heading_body = await ask_openai_validation_assistant(heading_prompt, max_tokens=100)
                if isinstance(heading_body, str) and heading_body.strip().lower() != "none":
                    heading = f"Repro IVF {heading_body}"
                prompt = f"Translate each item in this list to {language}. Put each item on a NEW LINE. Do NOT join them with semicolons. Each numbered item must start on its own line:\n{chr(10).join(services_list)}\nOutput: translated items, one per line"
                services_answer = await ask_openai_validation_assistant(prompt, max_tokens=500)
                if not isinstance(services_answer, str) or services_answer.strip().lower() == "none":
                    services_answer = "\n".join(services_list)
                else:
                    # Ensure proper newlines - replace semicolons with newlines if LLM used them
                    services_answer = services_answer.replace("; ", "\n").replace(";", "\n")
            llm_answer = heading + "\n" + services_answer
            if already_details_given:
                step_msg.insert(0, llm_answer)
            else:
                step_msg.insert(1, llm_answer)

        return step_msg, "add_on_service"
        # else:
        # return ["Sorry, the Pincode is invalid"," Please enter a valid pincode to check clinic availability near you"], None
    if step["step_id"] == "1":

        prompt = f"""
        You are a validation assistant.
        Conversation language = {language}.
        Step: {step_id}, Expecting: {step['expected_input']}
        The expected input can also be in user selected language.
        User input: "{user_message}"
        Valid condition (regex): {step['valid_condition']}
        Bot response must ALWAYS be written in {language}, regardless of input language or system language.


        2. Add-on service extraction & validation (for Step 1):
        - Extract the service/test mentioned in the user's question (e.g., from "What is embryo DNA testing? What does it cost?" extract "embryo DNA testing") and the user question can also be like all tests,extra tests or advanced tests and many more in which the user don't specify any test names but want to know all the tests then return None as test name and valid response.
        -** very IMP**-extract the medical test that the user wants to get from {user_message} only give test name no description about test or anything only test name output:string and if there is not test specified then return None and if user wants to know different type of test or extra tests or list of tests anything regarding different extra test then also return None and
        - If the message asks generally about tests, advanced tests, or types of tests or different tests or various tests or विभिन्न सेवाएँ or , return add_on_service "None" and status as valid and  bot_response-{step['message']} translated in {language}.
            Rules:
                    1. ***IMP**-If the user directly mentions a test name or service name and it exists in this list {allowed_add_on_services}, return that exact test name only.
                    2. If the user mentions a serial number (integer):
                    - Match the serial number exactly with the index/ID in {allowed_add_on_services}.
                    - Do NOT partially match numbers. For example: "20" MUST NOT match "2" or "0".
                    - If the serial number exists → return the corresponding test name only.
                    - If the serial number does not exist → return "None".
                    3. If the user provides a test name that is not present in the services mentioned above, return "None".
                    4. If the message is general and does not reference any specific test or number, return "None".
        - If it matches, → return status = "VALID", add_on_service = extracted service, bot_response = {step['message']} (translated into {language}).
        - If it does not match, → return status = "INVALID", add_on_service = "", bot_response = {step['other_text']} (translated into {language}).

        3. Regex + meaning validation (for other steps):
        - If input matches {step['valid_condition']} (regex + meaning check),
            then → return status = "VALID" and bot_response = {step['message']} (translated into {language}).

        4. Otherwise:
        - If input is not refusal and does not match regex,
            then → return status = "INVALID" and bot_response = {step['other_text']} (translated into {language}).

        - **Keep same format: if it is string then string; if list of strings then list of strings**


        *******Format for Step******** :
        Please Return response in this fromar only
        *****response = {{
            "status": "VALID" or "INVALID",
            "add_on_service": "the service/test asked by user (empty string if invalid)",
            "bot_response": "string or list of strings (next message to show the user in {language})"
        }}

         ***IMPOTANT***-Always return response in the above format only

        Rules:
        - Step 1: validate only against the allowed_add_on_services.
        - Other steps: use regex + meaning validation.
        - If not valid → status = "INVALID" and re-ask current step politely in {language}.
    """
    else:
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
    - If user input clearly expresses **refusal** (like "I don't want to give", "skip", "no", "nahi batana", "not sharing", "prefer not to say"),
        then → return only {step['final_text']} (translated into {language}), with status = "INVALID".
    - Do NOT treat unrelated or invalid inputs as refusal.
    2. Regex + meaning validation:
    - If the input matches {step['valid_condition']} (regex + meaning check),
        then → return status = "VALID" and bot_response = {step['message']} (translated into {language}).
    3. Otherwise:
    - If input is not refusal and does not match regex,
        then → return status = "INVALID" and bot_response = {step['other_text']} (translated into {language}).
    4-***you have to just translate the string in the language given below do not add anything extra from your side. Do NOT add any services list or test names - return ONLY the exact message specified above.
    - ** and also in same the format if it is string then string and if its is list of string then list of string

    Format:{{
            "status": "VALID" or "INVALID",
            "bot_response": "string or list of string  (next message to show the user in {language})",
        }}

    ***IMPOTANT***-Always return response in the above format only

    Rules:
    - If regex + meaning are correct → status = "VALID" and bot_response = next step message (filled with variables if available).
    - If not valid → status = "INVALID" and bot_response = re-ask current step politely in {language}.
    """

    llm_answer = await ask_openai_validation_assistant(prompt, max_tokens=1500)

    try:
        llm_json = json.loads(llm_answer)
    except Exception:
        try:
            llm_json = ast.literal_eval(llm_answer)
        # fallback if model doesn't output strict JSON
        except:
            llm_json = {"status": "INVALID", "bot_response": step["message"]}
    if step["step_id"] == "1":
        is_validated, answer = await validate_answer(
            llm_json,
            {
                "status": "INVALID",
                "add_on_service": "the service/test asked by user (empty string if invalid)"
                or None,
                "bot_response": step["message"],
            },
            language,
        )
        if not (is_validated):
            is_validated, answer = await validate_answer(
                llm_json,
                {
                    "status": "INVALID",
                    "add_on_service": "the service/test asked by user (empty string if invalid)"
                    or None,
                    "bot_response": step["other_text"],
                },
                language,
            )
            if not (is_validated):
                is_validated, answer = await validate_answer(
                    llm_json,
                    {
                        "status": "INVALID",
                        "add_on_service": "the service/test asked by user (empty string if invalid)"
                        or None,
                        "bot_response": step["final_text"],
                    },
                    language,
                )
                if not (is_validated):
                    return answer, "out_of_context"
    else:
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
    print(f"[ADD_ON_SERVICE] LLM result: step={step_id}, status={llm_json.get('status')}, bot_response={str(llm_json.get('bot_response'))[:200]}")
    if llm_json.get("status") == "INVALID":
        if thread and step["step_id"] == "1":
            thread.flow_id = None
            thread.step_id = None
            thread.previous_flow = thread.flow_id
            thread.previous_step = step["step_id"]
            await thread.save()
            return llm_json.get("bot_response"), "invalid"

    if llm_json.get("status") == "VALID":
        next_step = step["next_step"]
        if step["step_id"] == "1":
            user_info = await User_Info.find_one(User_Info.thread_id == thread_id)
            if user_info:
                user_info.preffered__medical_test = llm_json.get("add_on_service")
                await user_info.save()
            else:
                user_info = User_Info(
                    preffered__medical_test=llm_json.get("add_on_service"),
                    thread_id=thread_id,
                )
                await user_info.insert()
        if step["step_id"] == "2":
            user_info = await User_Info.find_one(User_Info.thread_id == thread_id)
            user_info.name = user_message
            await user_info.save()
        if step["step_id"] == "3":
            user_info = await User_Info.find_one(User_Info.thread_id == thread_id)
            user_info.phone_number = user_message
            user_info.preffered_center = [CLINIC_CENTER]
            await user_info.save()

            # Directly show services
            if thread:
                thread.flow_id = flow_id
                thread.step_id = None
                thread.step_count = 1
                thread.previous_flow = thread.flow_id
                thread.previous_step = step["step_id"]
                await thread.save()

            # Build service response
            step_msg = list(step["message"])  # copy

            # Translate static text messages for non-English languages
            if language != "English":
                for i, item in enumerate(step_msg):
                    if isinstance(item, str) and item.strip():
                        translated = await ask_openai_validation_assistant(
                            f"Translate this sentence to {language}, output only the translated sentence: '{item}' output-string", max_tokens=100
                        )
                        if isinstance(translated, str) and translated.strip().lower() != "none":
                            step_msg[i] = translated

            if user_info.preffered__medical_test and user_info.preffered__medical_test not in [
                "None",
                "none",
            ]:
                prompt = f"give a brief explaination about this test : {user_info.preffered__medical_test} in 10-20 wored in this language:{language} output-format:-string"
                llm_answer = await ask_openai_validation_assistant(
                    prompt, max_tokens=200
                )
                step_msg.insert(1, llm_answer)
            else:
                services_list = list(allowed_add_on_services)
                heading = "Repro IVF offers a variety of services and advanced tests to support fertility, pregnancy, and reproductive health. Here are some of the key ones:"
                if language == "English":
                    # No LLM needed for English - use the list directly
                    services_answer = "\n".join(services_list)
                else:
                    # Translate heading body (without brand name) and services list
                    heading_prompt = f"Translate this sentence to {language}, output only the translated sentence: 'offers a variety of services and advanced tests to support fertility, pregnancy, and reproductive health. Here are some of the key ones:' output-string"
                    heading_body = await ask_openai_validation_assistant(heading_prompt, max_tokens=100)
                    if isinstance(heading_body, str) and heading_body.strip().lower() != "none":
                        heading = f"Repro IVF {heading_body}"
                    prompt = f"Translate each item in this list to {language}. Put each item on a NEW LINE. Do NOT join them with semicolons. Each numbered item must start on its own line:\n{chr(10).join(services_list)}\nOutput: translated items, one per line"
                    services_answer = await ask_openai_validation_assistant(prompt, max_tokens=500)
                    if not isinstance(services_answer, str) or services_answer.strip().lower() == "none":
                        services_answer = "\n".join(services_list)
                    else:
                        services_answer = services_answer.replace("; ", "\n").replace(";", "\n")
                llm_answer = heading + "\n" + services_answer
                step_msg.insert(1, llm_answer)

            return step_msg, "add_on_service"

        # Save thread
        if thread:
            thread.flow_id = flow_id
            thread.step_id = next_step
            thread.step_count = 1
            thread.previous_flow = thread.flow_id
            thread.previous_step = step["step_id"]
            await thread.save()

        print(f"[ADD_ON_SERVICE] Returning: step={step_id}, next_step={next_step}, response={str(llm_json.get('bot_response'))[:200]}")
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
