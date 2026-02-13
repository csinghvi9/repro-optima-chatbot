from app.core.boto3client import bot_generate
import json
from app.models.threads import Thread
from bson import ObjectId
import ast
from app.core.format_check import validate_answer


async def EmotionalSupport(user_message, language: str, thread_id: str):
    # Explicitly keep messages as a list of separate strings
    messages = [
        "We understand this may be difficult for you. We just want you to know that our team is with you, every step of the way. Please feel free to reach out to us anytime on - +6332-256-2433.",
        "Hope this was helpful. Let me know if you need more info",
    ]

    prompt = f"""
                You are a helpful assistant. 
                User message: {user_message}  

                Your task:  

                - CASE 1: If the user asks about question such that they are really nervous, depressed or frightened or if they want emotional support:  
                • Translate the given `messages` list into {language} only in {language}.  
                • Keep the structure **identical** to {messages}.  
                don't give it as whole string in a list instead give the same structure as message a list and there it should have three strings in all language

                - CASE 2: If the user asks about anything unrelated to emotional support then:  
                • Return exactly this JSON (not merged with messages):  
                ["I can't help you on this. Is there anything else I can do?"]

               ⚠️ IMPORTANT:
                - Output MUST be valid JSON.
                - Use double quotes (") for strings, not single quotes (').
                - Do not wrap the whole list in quotes.
                -return the response in {language} only
                Input Messages:  
                {messages}  

                Output Format Example (CASE 1):
                ["<translated message>","<translated message>","<translated message>"]

                Output Format Example (CASE 2):
                ["I can't help you on this. Is there anything else I can do?"]

                 ***IMPOTANT***-Always return response in the above formats only
            """
    answer = await bot_generate(prompt, 500)

    try:
        parsed = json.loads(answer)  # first decode
        if isinstance(parsed, str):  # still a JSON string
            parsed = json.loads(parsed)  # decode again
        answer = parsed  # will give list
    except:
        try:
            answer = ast.literal_eval(answer)
        except Exception:
            answer = [answer]
    if isinstance(answer, list) and len(answer) > 1:
        is_validated, response = await validate_answer(answer, messages, language)
        if not (is_validated):
            return answer, "out_of_context"
    else:
        is_validated, answer = await validate_answer(
            answer,
            ["I can't help you on this. Is there anything else I can do?"],
            language,
        )
        if not (is_validated):
            return answer, "out_of_context"

    thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
    if thread:
        thread.flow_id = None
        thread.step_id = None
        thread.previous_flow = "emotional_support"
        thread.previous_step = thread.step_id
        await thread.save()
    return answer, None
