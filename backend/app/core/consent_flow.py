from app.models.threads import Thread
from app.utils.llm_utils import ask_openai_validation_assistant
from bson import ObjectId
import json
import ast
from app.core.format_check import validate_answer


async def ConsentFlow(
    thread_id: str, flow_id: str, step_id: str, language: str, user_message: str
):

    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)
    step_count = thread.step_count

    if thread and thread.step_id:
        step_id = thread.step_id
    elif not step_id:
        step_id = "1"

    consentflow = {
        "flow_id": "legal_consent",
        "steps": {
            "1": {
                "step_id": "1",
                "message": "Yes, both partners (or the individual) must sign consent forms before starting IVF.",
                "expected_input": "User asks that is there any legeal consent they have to signed or What legal documents are required prior to IVF? or why they have to signed etc",
                "action": None,
                "other_text": [
                    {
                        "first_text": "For more specific information, please connect with our call center between 9 AM and 6 PM.",
                        "second_text": "CUSTOMER CARE NUMBER",
                        "phone_number": "18003092323",
                    },
                    "Hope this helps! You can come back anytime to explore  or get more info",
                ],
                "next_step": "2",
            },
            "2": {
                "step_id": "2",
                "message": [
                    "The form covers IVF steps, embryo handling, storage period, future decisions (like donation or disposal), and your right to withdraw consent anytime",
                    "Hope this was helpful. Let me know if you need more info",
                ],
                "expected_input": "What’s included in the consent form? or what's inside the consent form? or what is in the form or what is written in the form etc or why we have to fill this form",
                "other_text": [
                    {
                        "first_text": "For more specific information, please connect with our call center between 9 AM and 6 PM.",
                        "second_text": "CUSTOMER CARE NUMBER",
                        "phone_number": "18003092323",
                    },
                    "Hope this helps! You can come back anytime to explore  or get more info",
                ],
                "action": None,
                "next_step": None,
            },
        },
    }

    step = consentflow["steps"].get(step_id)
    if not step:
        return {"error": "Invalid step"}

    if not user_message or user_message.strip() == "":
        user_message = ""

    prompt = f"""
You are NOT a chatbot.  
You are a strict JSON validation assistant.  
You never generate new text.  
You ONLY choose between two predefined outputs.  

Conversation language = {language}  
Step: {step_id}, Expecting: {step['expected_input']}  
User input: "{user_message}"  

Available responses:
- VALID response = {step['message']} → MUST be translated into {language}  
- INVALID response = {step['other_text']} → MUST be translated into {language}  

Rules:
1. If user input matches the expected meaning (even if paraphrased or in another language):  
   → Output: {{"status": "VALID", "bot_response": {step['message']} (translated to {language})}}  
2. **If user input does NOT match the expected meaning:  
   → Output: {{"status": "INVALID", "bot_response": {step['other_text']} (translated to {language} (do not translate the keys and dict))}}  
3. Do not create or generate your own answers. Copy ONLY from the predefined variables.  
4. Always respond strictly in valid JSON.  
5. The `bot_response` must always be fully in {language}. 
6. Do not merge response if it is invalid return return the invalid response defined above and if it is valid then return valid response only.

***IMPOTANT***-Always return response in the response format only

Now process the actual input:
"""

    # client = boto3.client("bedrock-runtime")
    # model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    # response = client.converse(
    #     modelId=model_id,
    #     messages=[{"role": "user", "content": [{"text": prompt}]}],
    #     inferenceConfig={"maxTokens": 500, "temperature": 0},
    # )

    llm_answer = await ask_openai_validation_assistant(prompt)

    try:
        # Try to load proper JSON
        llm_json = json.loads(llm_answer)
    except json.JSONDecodeError:
        try:
            # Try to handle pseudo-JSON with single quotes
            llm_json = ast.literal_eval(llm_answer)
        except Exception:
            # Fallback if both fail
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
            return answer, "out_of_context"

    if llm_json.get("status") == "INVALID":
        if thread:
            thread.step_count += 1
            await thread.save()
        return llm_json.get("bot_response"), "out_of_context"

    if llm_json.get("status") == "VALID":
        next_step = step["next_step"]

        if thread:
            thread.flow_id = flow_id
            thread.step_id = next_step
            thread.step_count = 1
            thread.previous_flow = thread.flow_id
            thread.previous_step = thread.step_id
            await thread.save()
        if step["step_id"] == "2":
            return llm_json.get("bot_response"), "feedback"
        return llm_json.get("bot_response"), None
    else:
        # stay on same step
        if thread and step["step_id"] == "1":
            next_step = step["next_step"]
            thread.flow_id = flow_id
            thread.step_id = next_step
            thread.step_count = 1
            thread.previous_flow = thread.flow_id
            thread.previous_step = thread.step_id
            await thread.save()
        return llm_json.get("bot_response"), None
