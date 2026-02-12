from app.models.threads import Thread
from bson import ObjectId
from app.core.boto3client import bot_generate
import json
import ast
from app.core.format_check import validate_answer


async def end_flow(thread_id: str, language: str, flow_change: bool = True):

    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)
    if flow_change:
        messages = "I do not understand your query, but I can only help with topics related to fertility, IVF, and Indira IVF services"
    else:
        messages = [
            "Sorry, I am unable to help you with this query currently. Please let me know if there's anything related to IVF which I can help you with.",
            {
                "first_text": "For more specific information, please connect with our call center between 9 AM and 6 PM.",
                "second_text": "CUSTOMER CARE NUMBER",
                "phone_number": "18003092323",
            },
            "Hope this helps!\n You can revisit us anytime for more information.",
        ]

    prompt = f"""You are a helpful assistant. 
Your only task is to respond with {messages}
translated into user language - {language}.
the first and second text in dictionary should also be translated

Return the result strictly as a JSON list of strings,  
keeping the same number of items as input.

***IMP***-do not translate the keys of the dict but translate the values and string in the message
and all should be in double quotes and the output structure should be same remeber this

Output Format Example:
["<translated message 1>","dict","<translated message 3>"] 
"""
    response = await bot_generate(prompt, 500)
    thread.flow_id = None
    thread.step_id = None
    thread.previous_flow = "out_of_context"
    thread.previous_step = thread.step_id
    await thread.save()
    try:
        llm_json = json.loads(response)
    except json.JSONDecodeError:
        try:
            llm_json = ast.literal_eval(response)
        except Exception:
            llm_json = response
    is_validated, answer = await validate_answer(llm_json, messages, language)
    if not (is_validated):
        return answer, "out_of_context"
    return llm_json, None
