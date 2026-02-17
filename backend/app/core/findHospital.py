from app.models.threads import Thread
from app.models.user_info import User_Info
from bson import ObjectId


CLINIC_CENTER = {
    "Clinic Name": "Repro Optima - Cebu City",
    "Address": "Ground Floor, JRDC Bldg, Osmeña Blvd, Cebu City, 6000 Cebu, Philippines",
    "City": "Cebu City",
    "State": "Cebu",
    "url": "https://www.google.com/maps?q=10.31264174367693,123.89200466249612",
}

HELP_TEXT_TRANSLATIONS = {
    "English": "Hope this was helpful. Let me know if you need more info",
    "Русский": "Надеюсь, это было полезно. Дайте мне знать, если вам нужна дополнительная информация",
    "Filipino": "Sana nakatulong ito. Ipaalam mo sa akin kung kailangan mo pa ng karagdagang impormasyon",
}

ADDRESS_LABEL_TRANSLATIONS = {
    "English": "Address",
    "Русский": "Адрес",
    "Filipino": "Address",
}


async def FindHospital(
    thread_id: str, flow_id: str, step_id: str, language: str, user_message: str
):
    find_hospital_flow = {
        "flow_id": "cost_and_package",
        "steps": {
            "1": {
                "step_id": "1",
                "message": "",
                "expected_input": "user wants to find nearby ivf centers",
                "action": "send_center_details",
                "next_step": "2",
            },
            "2": {
                "step_id": "2",
                "message": [
                    "",
                    "Hope this was helpful. Let me know if you need more info",
                ],
                "expected_input": "center_selection",
                "action": None,
                "next_step": None,
            },
        },
    }

    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)

    if thread and thread.step_id:
        step_id = thread.step_id
    elif not step_id:
        step_id = "1"

    step = find_hospital_flow["steps"].get(step_id)
    if not step:
        return {"error": "Invalid step"}

    # Step 1: Return the single hardcoded center immediately
    if step["step_id"] == "1":
        response = [CLINIC_CENTER]

        user = await User_Info.find_one(User_Info.thread_id == thread_id)
        if user:
            user.preffered_center = response
            await user.save()
        else:
            user_info = User_Info(
                preffered_center=response, thread_id=thread_id
            )
            await user_info.insert()

        next_step = step["next_step"]
        if thread:
            thread.flow_id = flow_id
            thread.step_id = next_step
            thread.previous_flow = thread.flow_id
            thread.previous_step = step["step_id"]
            await thread.save()

        return response, "centers"

    # Step 2: Handle center selection
    if step["step_id"] == "2":
        help_text = HELP_TEXT_TRANSLATIONS.get(language, HELP_TEXT_TRANSLATIONS["English"])
        address_label = ADDRESS_LABEL_TRANSLATIONS.get(language, ADDRESS_LABEL_TRANSLATIONS["English"])
        user = await User_Info.find_one(User_Info.thread_id == thread_id)
        response_msg = ["", help_text]
        if user and user.preffered_center:
            for c in user.preffered_center:
                clinic_name = c["Clinic Name"].strip().lower()
                user_input = user_message.strip().lower()
                if (
                    clinic_name == user_input
                    or clinic_name.split("-")[-1].strip() == user_input
                ):
                    user.preffered_center_address = c["Address"]
                    user.City = c["City"]
                    user.State = c["State"]
                    await user.save()
                    response_msg[0] = c["Clinic Name"] + "\n" + address_label + ": " + c["Address"]

        if thread:
            thread.flow_id = flow_id
            thread.step_id = step["next_step"]
            thread.previous_flow = thread.flow_id
            thread.previous_step = step["step_id"]
            await thread.save()

        return response_msg, "feedback"
