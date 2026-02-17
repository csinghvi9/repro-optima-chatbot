import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import json
import logging

# from app.cruds.message_cruds import create_message,get_all_messages
from app.cruds.threads_cruds import update_thread_name, get_thread_by_name
from app.core.websocket_init import WebSocketManager
from app.core.appointmentflow import appointment_flow
from app.core.end_flow import end_flow
from app.core.flow_classifier import flow_check, new_language_change
from fastapi import Query
from app.auth.jwt_handler import decode_jwt
import json
from app.core.lifestyleandpreparations import lifestyleAndPreparations
from bson import ObjectId
from app.models.threads import Thread
from app.core.emergencyContact import EmergencyContact
from app.core.ivfSuccessRate import IVFSuccessRate
from app.core.consent_flow import ConsentFlow
from app.core.ivf_steps import ivfSteps
from app.core.ivf_packages import ivfPackages
from app.core.emotionalSupport import EmotionalSupport
from app.core.medicalTerms import MedicalTerms
from app.core.cancelReschedule import cancelRescheduleFlow
from app.core.greetings import greetingsFlow
from app.core.faqflow import FAQFlow
from app.core.faqflow import query_vectorstore
from app.core.faqTabAnswer import faqTabAnswers
from app.core.findHospital import FindHospital
from app.core.addOnService import AddONServices
from app.models.message import Message
from app.core.language_change_flow import LanguageChange
from app.models.user_info import User_Info
from app.utils.config import ENV_PROJECT
from app.utils.llm_utils import ask_openai_validation_assistant


router = APIRouter()
websocket_manager = WebSocketManager()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket, token: str = Query(...)):
    logger.info(f"\U0001f7e1 Incoming WebSocket request with token: {token}")
    await websocket.accept()

    try:
        token = token.split(" ")[1]
        current_user = decode_jwt(token, ENV_PROJECT.GUEST_TOKEN_SECRET_KEY)
        logger.info(f"\u2705 Authenticated User: {current_user}")
    except Exception as e:
        logger.warning(f"\u274c JWT decode failed: {e}")
        await websocket.close(code=1008)
        return

    if not current_user:
        await websocket.close(code=1008)
        return

    user_id = current_user["user_id"]
    session_id = current_user["session_id"]

    await websocket_manager.connect(user_id, session_id, websocket)

    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)

            if data.get("type") == "message":
                content = data.get("message")
                # thread_id = active_connection["thread_id"]
                thread_id = data.get("thread_id")
                thread_obj_id = ObjectId(thread_id)
                thread = await Thread.find_one(Thread.id == thread_obj_id)
                flow_id = thread.flow_id
                step_id = thread.step_id
                language = thread.language
                messages = []
                if data.get("isflow") == "confirm":
                    thread.flow_id = data.get("subtype")
                    thread.step_id = None
                    await thread.save()
                    flow_id = data.get("subtype")
                    step_id = None
                else:
                    # Skip flow classifier if we're in a completed flow that handles center clicks
                    if flow_id in ["book_appointment", "nearby_centers"] and step_id == "6":
                        llm_flow_id = "None"
                    else:
                        llm_flow_id = await flow_check(content, language)
                    if llm_flow_id == "greetings" and thread.previous_flow in [
                        "book_appointment",
                        "ivf_steps",
                        "add_on_service",
                        "cost_and_package",
                    ]:
                        thread.flow_id = thread.previous_flow
                        thread.step_id = thread.previous_step
                        flow_id = thread.previous_flow
                        step_id = thread.previous_step
                        await thread.save()
                        latest_user_message = max(
                            (
                                m
                                for m in thread.messages
                                if m.role == "user"
                                and m.flow_id == thread.previous_flow
                            ),
                            key=lambda m: m.timestamp,
                            default=None,
                        )
                        if latest_user_message:
                            content = latest_user_message.content

                    elif llm_flow_id != "None":
                        if llm_flow_id != flow_id:
                            thread.flow_id = llm_flow_id
                            thread.step_id = None
                            # thread.previous_flow=thread.flow_id
                            # thread.previous_step=thread.step_id
                            flow_id = llm_flow_id
                            step_id = None
                            await thread.save()
                    elif (
                        llm_flow_id == "None"
                        and data.get("subtype") == ""
                        and not (flow_id)
                    ):
                        response, contentType = await end_flow(
                            thread_id, language, False
                        )
                        for i in range(len(response)):
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": (
                                            "out_of_context" if i == 1 else None
                                        ),
                                    }
                                )
                            )
                            messages.append(
                                {
                                    "response": response[i],
                                    "contentType": "out_of_context" if i == 1 else None,
                                }
                            )

                if not thread_id:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "text": "Please initialize a thread before sending messages.",
                            }
                        )
                    )
                    messages.append(
                        {
                            "response": "Please initialize a thread before sending messages.",
                            "contentType": None,
                        }
                    )
                    continue
                if content:
                    new_message = Message(
                        content=content,
                        role="user",  # or "assistant" depending on source
                        sender="user",
                        flow_id=flow_id,  # or however you identify sender
                    )
                    thread.messages.append(new_message)
                    await thread.save()
                if (
                    data.get("subtype") == "language_change"
                    or flow_id == "language_change"
                ):
                    response, contentType = await LanguageChange(
                        thread_id, flow_id, step_id, language, content
                    )
                    if contentType == "language_change":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "language_change",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "language_change"}
                        )
                    else:
                        if response:
                            thread = await Thread.find_one(
                                Thread.id == ObjectId(thread_id)
                            )
                            language = thread.language
                            thread.flow_id = thread.previous_flow
                            thread.step_id = thread.previous_step
                            flow_id = thread.previous_flow
                            step_id = thread.previous_step
                            await thread.save()
                            language = language
                            content = response
                            # new_thread=await Thread.find_one(Thread.id==ObjectId(thread_id))

                if (
                    data.get("subtype") == "book_appointment"
                    or flow_id == "book_appointment"
                ):
                    response, contentType = await appointment_flow(
                        thread_id, flow_id, step_id, language, content
                    )
                    if isinstance(response, list) and contentType == "calendar":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[0],
                                    "contentType": None,
                                }
                            )
                        )
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[1],
                                    "contentType": contentType,
                                }
                            )
                        )
                        for index, item in enumerate(response):
                            messages.append(
                                {
                                    "response": item,
                                    "contentType": contentType if index == 1 else None,
                                }
                            )

                    elif (
                        isinstance(response, list) and contentType == "invalid_feedback"
                    ):
                        for i, item in enumerate(response):
                            if i == 0 and len(response) != 1:
                                contentType = None
                            elif i == len(response) - 1:
                                contentType = "feedback"
                            else:
                                contentType = None
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": item,
                                        "contentType": contentType,
                                    }
                                )
                            )
                            messages.append(
                                {"response": item, "contentType": contentType}
                            )
                    elif isinstance(response, list) and contentType == "feedback":
                        for i, item in enumerate(response):
                            if i == 0:
                                contentType = "booked"
                            elif i == len(response) - 1:
                                contentType = "feedback"
                            else:
                                contentType = None
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": item,
                                        "contentType": contentType,
                                    }
                                )
                            )
                            messages.append(
                                {"response": item, "contentType": contentType}
                            )

                    elif isinstance(response, list) and contentType == "booked_with_centers":
                        # response = [clinic_data_list, booked_message_list]
                        # First send centers
                        centers_data = response[0]
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": centers_data,
                                    "contentType": "centers",
                                }
                            )
                        )
                        messages.append(
                            {"response": centers_data, "contentType": "centers"}
                        )
                        # Then send booked confirmation
                        booked_msg = response[1]
                        for i, item in enumerate(booked_msg):
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": item,
                                        "contentType": "booked" if i == 0 else None,
                                    }
                                )
                            )
                            messages.append(
                                {
                                    "response": item,
                                    "contentType": "booked" if i == 0 else None,
                                }
                            )
                    elif isinstance(response, list) and contentType == "booked":
                        for i, item in enumerate(response):
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": item,
                                        "contentType": contentType if i == 0 else None,
                                    }
                                )
                            )
                            messages.append(
                                {
                                    "response": item,
                                    "contentType": contentType if i == 0 else None,
                                }
                            )
                    elif contentType == "out_of_context":
                        if isinstance(response, list):
                            for i, item in enumerate(response):
                                await websocket.send_text(
                                    json.dumps(
                                        {
                                            "type": "message",
                                            "text": item,
                                            "contentType": (
                                                "out_of_context" if i == 0 else None
                                            ),
                                        }
                                    )
                                )
                                messages.append(
                                    {
                                        "response": item,
                                        "contentType": (
                                            "out_of_context" if i == 0 else None
                                        ),
                                    }
                                )
                        else:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response,
                                        "contentType": "out_of_context",
                                    }
                                )
                            )
                            messages.append(
                                {"response": response, "contentType": "out_of_context"}
                            )
                    elif isinstance(response, list) and contentType != "centers":
                        for message in response:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": message,
                                        "contentType": contentType,
                                    }
                                )
                            )
                            messages.append(
                                {"response": message, "contentType": contentType}
                            )
                    else:
                        # handle single response or centers separately if needed
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": contentType,
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": contentType}
                        )
                elif (data.get("subtype") == "Lifestyle_and_Preparations") or (
                    flow_id == "Lifestyle_and_Preparations"
                ):
                    response, contentType = await lifestyleAndPreparations(
                        language, thread_id
                    )
                    if contentType == "out_of_context":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "out_of_context",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "out_of_context"}
                        )
                    else:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[0],
                                    "contentType": "Lifestyle_and_Preparations",
                                }
                            )
                        )
                        messages.append(
                            {
                                "response": response[0],
                                "contentType": "Lifestyle_and_Preparations",
                            }
                        )
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[1],
                                    "contentType": None,
                                }
                            )
                        )
                        messages.append({"response": response[1], "contentType": None})
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[2],
                                    "contentType": "book_appointment",
                                }
                            )
                        )
                        messages.append({"response": response[2], "contentType": None})
                elif (data.get("subtype") == "emergency_contact") or (
                    flow_id == "emergency_contact"
                ):
                    response, contentType = await EmergencyContact(
                        content, language, thread_id
                    )
                    if contentType == "out_of_context":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "out_of_context",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "out_of_context"}
                        )
                    else:
                        for i in range(len(response)):
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": "emergency_contact",
                                    }
                                )
                            )
                            messages.append(
                                {
                                    "response": response[i],
                                    "contentType": "emergency_contact",
                                }
                            )
                elif (data.get("subtype") == "success_rate") or (
                    flow_id == "success_rate"
                ):
                    response, contentType = await IVFSuccessRate(
                        content, language, thread_id
                    )
                    if contentType == "out_of_context":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "out_of_context",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "out_of_context"}
                        )
                    else:
                        if len(response) == 2:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[0],
                                        "contentType": "success_rate",
                                    }
                                )
                            )
                            messages.append(
                                {"response": response[0], "contentType": "success_rate"}
                            )
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[1],
                                        "contentType": "ivf_calculate",
                                    }
                                )
                            )
                            messages.append(
                                {
                                    "response": response[1],
                                    "contentType": "ivf_calculate",
                                }
                            )
                        else:
                            if isinstance(response[0], dict):
                                for i in response:
                                    if isinstance(i, dict):
                                        await websocket.send_text(
                                            json.dumps(
                                                {
                                                    "type": "message",
                                                    "text": i,
                                                    "contentType": "success_rate",
                                                }
                                            )
                                        )
                                        messages.append(
                                            {
                                                "response": i,
                                                "contentType": "success_rate",
                                            }
                                        )
                                    else:
                                        await websocket.send_text(
                                            json.dumps(
                                                {
                                                    "type": "message",
                                                    "text": i,
                                                    "contentType": "ivf_calculate",
                                                }
                                            )
                                        )
                                        messages.append(
                                            {
                                                "response": i,
                                                "contentType": "ivf_calculate",
                                            }
                                        )
                            else:
                                for i in response:
                                    await websocket.send_text(
                                        json.dumps(
                                            {
                                                "type": "message",
                                                "text": i,
                                                "contentType": None,
                                            }
                                        )
                                    )
                                    messages.append(
                                        {"response": i, "contentType": None}
                                    )

                elif data.get("subtype") == "ivf_steps" or flow_id == "ivf_steps":
                    response, contentType = await ivfSteps(
                        thread_id, flow_id, step_id, language, content
                    )
                    if isinstance(response, list) and contentType == "ivf_steps":
                        target_index = 2 if len(response) == 5 else 1
                        for i in range(len(response)):
                            if i == len(response) - 1:
                                contentType = "feedback"
                            elif i == target_index:
                                contentType = "ivf_steps"
                            else:
                                contentType = None
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": contentType,
                                    }
                                )
                            )
                            messages.append(
                                {"response": response[i], "contentType": contentType}
                            )
                    elif (
                        isinstance(response, list) and contentType == "invalid_feedback"
                    ):
                        for i, item in enumerate(response):
                            if i == 0 and len(response) != 1:
                                contentType = None
                            elif i == len(response) - 1:
                                contentType = "feedback"
                            else:
                                contentType = None
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": item,
                                        "contentType": contentType,
                                    }
                                )
                            )
                            messages.append(
                                {"response": item, "contentType": contentType}
                            )
                    elif contentType == "out_of_context":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "out_of_context",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "out_of_context"}
                        )
                    elif isinstance(response, list):
                        for i in response:
                            await websocket.send_text(
                                json.dumps(
                                    {"type": "message", "text": i, "contentType": None}
                                )
                            )
                            messages.append({"response": i, "contentType": None})

                    else:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": None,
                                }
                            )
                        )
                        messages.append({"response": response, "contentType": None})
                elif (
                    data.get("subtype") == "cost_and_package"
                    or flow_id == "cost_and_package"
                ):
                    response, contentType = await ivfPackages(
                        thread_id, flow_id, step_id, language, content
                    )
                    if isinstance(response, list) and contentType == "cost_and_package":
                        target_index = 2 if len(response) == 4 else 1
                        for i in range(len(response)):
                            if i == target_index:
                                content_type = "cost_and_package"
                            elif i == (target_index + 1):
                                content_type = "book_appointment"
                            else:
                                content_type = None

                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": content_type,
                                    }
                                )
                            )
                            messages.append(
                                {"response": response[i], "contentType": content_type}
                            )

                    elif (
                        isinstance(response, list) and contentType == "invalid_feedback"
                    ):
                        for i, item in enumerate(response):
                            if i == 0 and len(response) != 1:
                                contentType = None
                            elif i == len(response) - 1:
                                contentType = "feedback"
                            else:
                                contentType = None
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": item,
                                        "contentType": contentType,
                                    }
                                )
                            )
                            messages.append(
                                {"response": item, "contentType": contentType}
                            )
                    elif contentType == "out_of_context":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "out_of_context",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "out_of_context"}
                        )
                    elif isinstance(response, list):
                        for i in response:
                            await websocket.send_text(
                                json.dumps(
                                    {"type": "message", "text": i, "contentType": None}
                                )
                            )
                            messages.append({"response": i, "contentType": None})

                    else:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": None,
                                }
                            )
                        )
                        messages.append({"response": response, "contentType": None})
                elif (data.get("subtype") == "emotional_support") or (
                    flow_id == "emotional_support"
                ):
                    response, contentType = await EmotionalSupport(
                        content, language, thread_id
                    )
                    if contentType == "out_of_context":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "out_of_context",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "out_of_context"}
                        )
                    else:
                        for i in range(len(response)):
                            if i == len(response) - 1:
                                contentType = "feedback"
                            elif i == 1:
                                contentType = "whats_app"
                            elif i == 0:
                                contentType = "emotional_support"
                            else:
                                contentType = None
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": contentType,
                                    }
                                )
                            )
                            messages.append(
                                {"response": response[i], "contentType": contentType}
                            )

                elif (data.get("subtype") == "out_of_context") or (
                    flow_id == "out_of_context"
                ):
                    queries = await query_vectorstore(content, language)
                    if queries:
                        thread.flow_id = llm_flow_id
                        thread.step_id = None
                        thread.previous_flow = thread.flow_id
                        thread.previous_step = thread.step_id
                        flow_id = llm_flow_id
                        step_id = None
                        await thread.save()
                        response, isrelevant = await FAQFlow(
                            content, language, thread_id, queries
                        )
                        if isrelevant:
                            if isinstance(response, list):
                                for i in range(len(response)):
                                    if i == 0:
                                        contentType = "faqflow"
                                    else:
                                        contentType = None

                                    await websocket.send_text(
                                        json.dumps(
                                            {
                                                "type": "message",
                                                "text": response[i],
                                                "contentType": contentType,
                                            }
                                        )
                                    )
                                    messages.append(
                                        {
                                            "response": response[i],
                                            "contentType": contentType,
                                        }
                                    )
                            else:
                                await websocket.send_text(
                                    json.dumps(
                                        {
                                            "type": "message",
                                            "text": response,
                                            "contentType": "faqflow",
                                        }
                                    )
                                )
                                messages.append(
                                    {"response": response, "contentType": "faqflow"}
                                )

                        else:
                            if isinstance(response, list):
                                for i in range(len(response)):
                                    if isinstance(response[i], dict):
                                        contentType = "out_of_context"
                                    else:
                                        contentType = None
                                    await websocket.send_text(
                                        json.dumps(
                                            {
                                                "type": "message",
                                                "text": response[i],
                                                "contentType": contentType,
                                            }
                                        )
                                    )
                                    messages.append(
                                        {
                                            "response": response[i],
                                            "contentType": contentType,
                                        }
                                    )
                            else:
                                await websocket.send_text(
                                    json.dumps(
                                        {
                                            "type": "message",
                                            "text": response,
                                            "contentType": "invalid_feedback",
                                        }
                                    )
                                )
                                messages.append(
                                    {
                                        "response": response,
                                        "contentType": "invalid_feedback",
                                    }
                                )

                    else:
                        response, contentType = await end_flow(thread_id, language)
                        if contentType == "out_of_context":
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response,
                                        "contentType": "out_of_context",
                                    }
                                )
                            )
                            messages.append(
                                {"response": response, "contentType": "out_of_context"}
                            )
                        else:
                            for i in range(len(response)):
                                await websocket.send_text(
                                    json.dumps(
                                        {
                                            "type": "message",
                                            "text": response[i],
                                            "contentType": (
                                                "out_of_context" if i == 1 else None
                                            ),
                                        }
                                    )
                                )
                                messages.append(
                                    {
                                        "response": response[i],
                                        "contentType": (
                                            "out_of_context" if i == 1 else None
                                        ),
                                    }
                                )
                elif (data.get("subtype") == "cancel_or_reschedule") or (
                    flow_id == "cancel_or_reschedule"
                ):
                    response, contentType = await cancelRescheduleFlow(
                        thread_id, language, content
                    )
                    if contentType == "out_of_context":
                        if isinstance(response, list):
                            for i in range(len(response)):
                                await websocket.send_text(
                                    json.dumps(
                                        {
                                            "type": "message",
                                            "text": response[i],
                                            "contentType": (
                                                "out_of_context" if i == 0 else None
                                            ),
                                        }
                                    )
                                )
                                messages.append(
                                    {
                                        "response": response[i],
                                        "contentType": (
                                            "out_of_context" if i == 0 else None
                                        ),
                                    }
                                )
                        else:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response,
                                        "contentType": "out_of_context",
                                    }
                                )
                            )
                            messages.append(
                                {"response": response, "contentType": "out_of_context"}
                            )
                    else:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": contentType,
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": contentType}
                        )

                elif (
                    data.get("subtype") == "medical_terms" or flow_id == "medical_terms"
                ):
                    response = await MedicalTerms(content, language, thread_id)
                    if isinstance(response, list):
                        for i in response:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": i,
                                        "contentType": "medical_terms",
                                    }
                                )
                            )
                            messages.append(
                                {"response": i, "contentType": "medical_terms"}
                            )
                    else:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "medical_terms",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "medical_terms"}
                        )
                elif data.get("subtype") == "greetings" or flow_id == "greetings":
                    response = await greetingsFlow(content, language, thread_id)
                    if isinstance(response, list):
                        for i in response:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": i,
                                        "contentType": "greetings",
                                    }
                                )
                            )
                            messages.append({"response": i, "contentType": "greetings"})
                    else:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "greetings",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "greetings"}
                        )

                elif (data.get("subtype") == "legal_consent") or (
                    flow_id == "legal_consent"
                ):
                    response, contentType = await ConsentFlow(
                        thread_id, flow_id, step_id, language, content
                    )
                    if contentType == "out_of_context":
                        if isinstance(response, list):
                            for i in range(len(response)):
                                await websocket.send_text(
                                    json.dumps(
                                        {
                                            "type": "message",
                                            "text": response[i],
                                            "contentType": (
                                                "out_of_context" if i == 0 else None
                                            ),
                                        }
                                    )
                                )
                                messages.append(
                                    {
                                        "response": response[i],
                                        "contentType": (
                                            "out_of_context" if i == 0 else None
                                        ),
                                    }
                                )
                        else:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response,
                                        "contentType": "out_of_context",
                                    }
                                )
                            )
                            messages.append(
                                {"response": response, "contentType": "out_of_context"}
                            )
                    elif isinstance(response, list) and contentType == "feedback":
                        for i in response:
                            if i == len(response) - 1:
                                contentType = contentType
                            else:
                                contentType = None
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": i,
                                        "contentType": contentType,
                                    }
                                )
                            )
                            messages.append({"response": i, "contentType": contentType})
                    elif isinstance(response, list):
                        for i in response:
                            await websocket.send_text(
                                json.dumps(
                                    {"type": "message", "text": i, "contentType": None}
                                )
                            )
                            messages.append({"response": i, "contentType": None})
                    else:
                        # handle single response or centers separately if needed
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": contentType,
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": contentType}
                        )
                elif (data.get("subtype") == "faq_flow") or (flow_id == "faq_flow"):
                    response, isrelevant = await FAQFlow(content, language, thread_id)
                    if isinstance(response, list) and data.get("isflow") == "confirm":
                        for i in range(len(response)):
                            if isinstance(response[i], dict):
                                contentType = "out_of_context"
                            else:
                                contentType = None
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": (
                                            "ivf_question" if i == 0 else contentType
                                        ),
                                    }
                                )
                            )
                            messages.append(
                                {
                                    "response": response[i],
                                    "contentType": (
                                        "ivf_question" if i == 0 else contentType
                                    ),
                                }
                            )
                    elif data.get("isflow") == "confirm":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "ivf_question",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "ivf_question"}
                        )
                    elif isrelevant:
                        if isinstance(response, list):
                            for i in range(len(response)):
                                if i == 0:
                                    contentType = "faqflow"
                                else:
                                    contentType = None
                                await websocket.send_text(
                                    json.dumps(
                                        {
                                            "type": "message",
                                            "text": response[i],
                                            "contentType": contentType,
                                        }
                                    )
                                )
                                messages.append(
                                    {
                                        "response": response[i],
                                        "contentType": contentType,
                                    }
                                )
                        else:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response,
                                        "contentType": "faqflow",
                                    }
                                )
                            )
                            messages.append(
                                {"response": response, "contentType": "faqflow"}
                            )
                    else:
                        if isinstance(response, list):
                            for i in range(len(response)):
                                if isinstance(response[i], dict):
                                    contentType = "out_of_context"
                                else:
                                    contentType = None
                                await websocket.send_text(
                                    json.dumps(
                                        {
                                            "type": "message",
                                            "text": response[i],
                                            "contentType": contentType,
                                        }
                                    )
                                )
                                messages.append(
                                    {
                                        "response": response[i],
                                        "contentType": contentType,
                                    }
                                )
                        else:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response,
                                        "contentType": "invalid_feedback",
                                    }
                                )
                            )
                            messages.append(
                                {
                                    "response": response,
                                    "contentType": "invalid_feedback",
                                }
                            )

                elif (data.get("subtype") == "frequently_asked_questions") or (
                    flow_id == "frequently_asked_questions"
                ):
                    response, contentType = await faqTabAnswers(language)
                    if contentType == "out_of_context":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "out_of_context",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "out_of_context"}
                        )
                    else:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "frequently_asked_questions",
                                }
                            )
                        )
                        messages.append(
                            {
                                "response": response,
                                "contentType": "frequently_asked_questions",
                            }
                        )
                    thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
                    if thread:
                        thread.flow_id = None
                        thread.step_id = None
                        thread.previous_flow = "frequently_asked_question"
                        thread.previous_step = thread.step_id
                        await thread.save()

                elif (data.get("subtype") == "add_on_service") or (
                    flow_id == "add_on_service"
                ):
                    response, contentType = await AddONServices(
                        thread_id, flow_id, step_id, language, content
                    )
                    if isinstance(response, list) and contentType == "add_on_service":
                        target_index = 2 if len(response) == 3 else 1
                        for i in range(len(response)):
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": (
                                            "add_on_service"
                                            if i == target_index
                                            else None
                                        ),
                                    }
                                )
                            )
                            messages.append(
                                {
                                    "response": response[i],
                                    "contentType": (
                                        "add_on_service" if i == target_index else None
                                    ),
                                }
                            )
                    elif isinstance(response, list) and contentType == "invalid":
                        for i in range(len(response)):
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": (
                                            "out_of_context" if i == 1 else None
                                        ),
                                    }
                                )
                            )
                            messages.append(
                                {
                                    "response": response[i],
                                    "contentType": "out_of_context" if i == 1 else None,
                                }
                            )
                    elif (
                        isinstance(response, list) and contentType == "invalid_feedback"
                    ):
                        for i, item in enumerate(response):
                            if i == 0 and len(response) != 1:
                                contentType = None
                            elif i == len(response) - 1:
                                contentType = "feedback"
                            else:
                                contentType = None
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": item,
                                        "contentType": contentType,
                                    }
                                )
                            )
                            messages.append(
                                {"response": item, "contentType": contentType}
                            )
                    elif contentType == "out_of_context":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "out_of_context",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "out_of_context"}
                        )
                    elif isinstance(response, list):
                        for i in range(len(response)):
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": None,
                                    }
                                )
                            )
                            messages.append(
                                {"response": response[i], "contentType": None}
                            )
                    else:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": None,
                                }
                            )
                        )
                        messages.append({"response": response, "contentType": None})

                elif (data.get("subtype") == "nearby_centers") or (
                    flow_id == "nearby_centers"
                ):
                    response, contentType = await FindHospital(
                        thread_id, flow_id, step_id, language, content
                    )
                    if isinstance(response, list) and contentType == "feedback":
                        for i, item in enumerate(response):
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": item,
                                        "contentType": (
                                            contentType
                                            if i == len(response) - 1
                                            else None
                                        ),
                                    }
                                )
                            )
                            messages.append(
                                {
                                    "response": item,
                                    "contentType": (
                                        contentType if i == len(response) - 1 else None
                                    ),
                                }
                            )
                    elif (
                        isinstance(response, list) and contentType == "invalid_feedback"
                    ):
                        for i, item in enumerate(response):
                            if i == 0 and len(response) != 1:
                                contentType = None
                            elif i == len(response) - 1:
                                contentType = "feedback"
                            else:
                                contentType = None
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": item,
                                        "contentType": contentType,
                                    }
                                )
                            )
                            messages.append(
                                {"response": item, "contentType": contentType}
                            )
                    elif contentType == "out_of_context":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": "out_of_context",
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": "out_of_context"}
                        )
                    elif isinstance(response, list) and contentType != "centers":
                        for i in range(len(response)):
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": contentType,
                                    }
                                )
                            )
                            messages.append(
                                {"response": response[i], "contentType": contentType}
                            )
                    else:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": contentType,
                                }
                            )
                        )
                        messages.append(
                            {"response": response, "contentType": contentType}
                        )

                else:
                    response = None

                if messages:
                    thread = await Thread.find_one(Thread.id == thread_obj_id)
                    for msg in messages:
                        new_message = Message(
                            content=msg.get("response"),
                            role="bot",  # or "assistant" depending on source
                            sender="bot",
                            contentType=msg.get(
                                "contentType"
                            ),  # or however you identify sender
                        )
                        thread.messages.append(new_message)
                    await thread.save()

                thread_name = await get_thread_by_name(thread_id)
                if thread_name == "New Chat":
                    if data.get("subtype") == "appointment":
                        chat_name = "Booking an Appointment"
                    elif data.get("subtype") == "clinic":
                        chat_name = "Finding Near By Center"
                    else:
                        chat_name = "General Enquiry"
                    await update_thread_name(thread_id, chat_name)
                # await websocket.send_text(
                #         json.dumps({"type": "message", "text": response})
                #     )

            elif data.get("type") == "update-thread":
                await websocket_manager.broadcast_to_all_sessions(
                    user_id, "New thread created or updated!"
                )

            elif data.get("type") == "login_success":
                pass

    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id, session_id)
