from app.core.boto3client import bot_generate
import json
from app.models.threads import Thread
from bson import ObjectId
import ast
from app.core.format_check import validate_answer


async def EmergencyContact(user_message, language: str, thread_id: str):

    # Explicitly keep messages as a list of separate strings
    messages = [
        {
            "heading": "EMERGENCY NUMBER",
            "phone_number": "+6332-256-2433",
            "text": "In case of any emergency, feel free to call this number between 9 AM and 6 PM.",
        },
    ]

    prompt = f"""
                You are a helpful assistant.
                user message = {user_message}

                Your task:
                - If the user asks about emergency contacts, translate the messages into {language}.
                - In the dictionary, translate only the `heading` and `text` fields into {language},
                but keep the `phone_number` exactly the same.
                - If the user asks irrelevant or unwanted questions not related to emergency contact, return:
                ["Please call on the emergency number provided above. Is there anything else I can do?"]

                Return the result strictly as a JSON list,
                keeping the same structure (list with one dict).

                Input Messages:
                {messages}

                Output Format Example:
                [{{"heading":"<translated heading>", "phone_number":"+6332-256-2433", "text":"<translated text>"}}]

                ***IMPOTANT***-Always return response in the above format only
            """

    answer = await bot_generate(prompt, 500)

    try:
        answer = json.loads(answer)  # will give list
    except:
        try:
            answer = ast.literal_eval(answer)
        except Exception:
            try:
                answer = ast.literal_eval(answer)
            except Exception:
                answer = [answer]
    is_validated, response = await validate_answer(answer, messages, language)
    if not (is_validated):
        return response, "out_of_context"

    thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
    if thread:
        thread.flow_id = None
        thread.step_id = None
        thread.previous_flow = "emergency_contact"
        thread.previous_step = thread.step_id
        await thread.save()
    return answer, None
