from app.core.boto3client import bot_generate
import json
import ast
from app.models.threads import Thread
from bson import ObjectId
from app.core.format_check import validate_answer


async def ivf_success_calculation_flow(language: str, thread_id):
    thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
    # Explicitly keep messages as a list of separate strings
    messages = [
        "We have devised an Pregnancy Calculator which gives success rate based on historical data of IVF.",
        "This is how our Pregnancy Calculator works.\n1 Share details and reports\n2 We analyze key fertility factors\n3 Know success rate for each cycle",
    ]

    # No need to join — instead pass list directly in prompt
    prompt = f"""
You are a helpful assistant.  
Translate each of the following items into {language}.  
Return the result strictly as a JSON list of strings,  
keeping the same number of items as input.
and don't add anything from your side

Input Messages:
{messages}

Output Format Example:
["<translated message 1>", "<translated message 2>"]

***IMPOTANT***-Always return response in the above format only

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

    if thread:
        thread.flow_id = None
        thread.step_id = None
        thread.previous_flow = "ivf_success_calculator"
        thread.previous_step = thread.step_id
        await thread.save()
    return answer, None
