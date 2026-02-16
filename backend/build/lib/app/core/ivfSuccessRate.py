from app.core.boto3client import bot_generate
import json
from app.models.threads import Thread
from bson import ObjectId
import ast
from app.core.format_check import validate_answer


async def IVFSuccessRate(user_message, language: str, thread_id: str):

    # Explicitly keep messages as a list of separate strings
    # prompt = f"You are a strict keyword-based classifier. If the user message contains “IUI”, “Intrauterine Insemination”, or any language-specific equivalent referring to IUI, including questions about IUI success rate or the success rate of any clinic (for example, IVF) in relation to IUI, output iui. If the user message contains the word “natural” (in any language) and asks about natural pregnancy or natural conception success rate, output natural. If the message asks about success rate related to “IVF”, “In Vitro Fertilization”, or any language-specific equivalent of IVF, output ivf. Do not infer intent or meaning beyond explicit keywords or full-form terms. If none of the above keywords or full forms appear, default to ivf. Respond with ONLY one word: iui, natural, or ivf. user_message={user_message} output:String"
    # answer = await bot_generate(prompt, 10)
    # if answer.lower() == "iui":
    iui_messages = [
        {
            "first_text": "We report a success rate of around 13-15% per cycle",
            "second_heading": "10,000 +",
            "second_text": "Couples found happiness",
        },
    ]
    # elif answer.lower() == "ivf":
    messages = [
        {
            "first_text": "We report a success rate of around 70-75% per cycle",
            "second_heading": "10,000 +",
            "second_text": "Couples found happiness",
        },
    ]
    # else:
    natural_messages = [
        {
            "first_text": "We report a success rate of around 70-75% per cycle",
            "second_heading": "10,000 +",
            "second_text": "Couples found happiness",
        },
    ]

    prompt = f"""
                You are a helpful assistant.
                User message: {user_message}

                Your task:

                - CASE 1: If the user asks about success rate, successful cases, couples, or related information:
                • Translate the given `messages` list into {language}.
                • Only translate the values of `first_text`, `second_heading`, `second_text`.
                • Keep numbers/digits exactly the same.
                • You are a strict keyword-based classifier. If the user message contains "IUI", "Intrauterine Insemination", or any language-specific equivalent referring to IUI, including questions about IUI success rate or the success rate of any clinic (for example, IVF) in relation to IUI, then return this message{iui_messages}. If the user message contains the word "natural" (in any language) and asks about natural pregnancy or natural conception success rate, output this sets of messages {natural_messages}. If the message asks about success rate related to "IVF", "In Vitro Fertilization", or any language-specific equivalent of IVF, output {messages}. Do not infer intent or meaning beyond explicit keywords or full-form terms. If none of the above keywords or full forms appear, default to {messages}. .
                • ***Keep the structure **identical** and the structure should be [dict].

                - CASE 2: If the user asks about failure rate, failures, or anything irrelevant about IVF:
                • Return exactly this JSON (not merged with messages):
                ["I can't help you on this. Is there anything else I can do?"]

                ⚠️ STRICT RULES:
                - Output must be **only valid JSON**.
                - Do not add explanations, labels, or extra text.
                - The output must be **either** the translated `messages` list **or** the failure JSON, nothing else.

                Output Format Example (CASE 1):
                [{{"first_text": "...", "second_heading": "...", "second_text": "..."}}]

                Output Format Example (CASE 2):
                ["I can't help you on this. Is there anything else I can do?"]
            """
    answer = await bot_generate(prompt, 500)

    try:
        answer = json.loads(answer)  # will give list
    except:
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
        thread.previous_flow = "success_rate"
        thread.previous_step = thread.step_id
        await thread.save()
    return answer, None
