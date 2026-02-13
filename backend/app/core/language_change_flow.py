from app.models.threads import Thread
from app.utils.llm_utils import ask_openai_validation_assistant
from bson import ObjectId
import json
import ast


async def LanguageChange(
    thread_id: str, flow_id: str, step_id: str, language: str, user_message: str
):

    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)

    if thread and thread.step_id:
        step_id = thread.step_id
    elif not step_id:
        step_id = "1"

    languageflow = {
        "flow_id": "language_change",
        "steps": {
            "1": {
                "step_id": "1",
                "message": "Please select the preferred language",
                "expected_input": "User wants to change the Language or the user is asking the bot to answer in a particular language",
                "action": None,
                "other_text": [
                    {
                        "first_text": "For more specific information, please connect with our call center between 9 AM and 6 PM.",
                        "second_text": "CUSTOMER CARE NUMBER",
                        "phone_number": "+6332-256-2433",
                    },
                    "Hope this helps! You can come back anytime to explore  or get more info",
                ],
                "next_step": "2",
            },
            "2": {
                "step_id": "2",
                "message": "",
                "expected_input": "",
                "other_text": [],
                "action": None,
                "next_step": None,
            },
        },
    }

    step = languageflow["steps"].get(step_id)
    if not step:
        return {"error": "Invalid step"}

    if not user_message or user_message.strip() == "":
        user_message = ""

    if step["step_id"] == "1":

        if thread:
            thread.flow_id = flow_id
            thread.step_id = step["next_step"]
            await thread.save()
        return step["message"], flow_id
    else:
        if user_message in [
            "English",
            "हिन्दी",
            "मराठी",
            "ગુજરાતી",
            "ಕನ್ನಡ",
            "বাংলা",
            "தமிழ்",
            "ਪੰਜਾਬੀ",
            "অসমীয়া",
            "ଓଡ଼ିଆ",
            "తెలుగు",
        ]:
            if thread:
                thread.language = user_message
                await thread.save()
            latest_user_message = max(
                (
                    m
                    for m in thread.messages
                    if m.role == "user" and m.flow_id == thread.previous_flow
                ),
                key=lambda m: m.timestamp,
                default=None,
            )
            if latest_user_message:
                content = latest_user_message.content
            else:
                content = None
            return content, None
        else:
            step = languageflow["steps"].get("1")
            if thread:
                thread.flow_id = flow_id
                thread.step_id = step["next_step"]
                await thread.save()
            return step["message"], flow_id


#     prompt = f"""
# You are NOT a chatbot.
# You are a strict JSON validation assistant.
# You never generate new text.
# You ONLY choose between two predefined outputs.

# Conversation language = {language}
# Step: {step_id}, Expecting: {step['expected_input']}
# User input: "{user_message}"

# Available responses:
# - VALID response = {step['message']} → MUST be translated into {language}
# - INVALID response = {step['other_text']} → MUST be translated into {language}

# Rules:
# 1. If user input matches the expected meaning (even if paraphrased or in another language):
#    → Output: {{"status": "VALID", "bot_response": {step['message']} (translated to {language})}}
# 2. **If user input does NOT match the expected meaning:
#    → Output: {{"status": "INVALID", "bot_response": {step['other_text']} (translated to {language} (do not translate the keys and dict))}}
# 3. Do not create or generate your own answers. Copy ONLY from the predefined variables.
# 4. Always respond strictly in valid JSON.
# 5. The `bot_response` must always be fully in {language}.
# 6. Do not merge response if it is invalid return return the invalid response defined above and if it is valid then return valid response only.


# Now process the actual input:
# """

#     # client = boto3.client("bedrock-runtime")
#     # model_id = "anthropic.claude-3-haiku-20240307-v1:0"

#     # response = client.converse(
#     #     modelId=model_id,
#     #     messages=[{"role": "user", "content": [{"text": prompt}]}],
#     #     inferenceConfig={"maxTokens": 500, "temperature": 0},
#     # )

#     llm_answer = await ask_openai_validation_assistant(prompt)
#     print("raw llm answer:", llm_answer)

#     try:
#     # Try to load proper JSON
#         llm_json = json.loads(llm_answer)
#     except json.JSONDecodeError:
#         try:
#             # Try to handle pseudo-JSON with single quotes
#             llm_json = ast.literal_eval(llm_answer)
#         except Exception:
#             # Fallback if both fail
#             llm_json = {"status": "INVALID", "bot_response": step["message"]}

#     print("llm json ", llm_json)
#     if llm_json.get("status") == "INVALID":
#         if thread:
#             thread.step_count += 1
#             await thread.save()
#         return llm_json.get("bot_response"), "out_of_context"

#     if llm_json.get("status") == "VALID":
#         next_step = step["next_step"]
#         print("next step is", next_step)

#         if thread:
#             thread.flow_id = flow_id
#             thread.step_id = next_step
#             thread.step_count = 1
#             thread.previous_flow=thread.flow_id
#             thread.previous_step=thread.step_id
#             await thread.save()
#         if step["step_id"]=="2":
#             return llm_json.get("bot_response"), "feedback"
#         return llm_json.get("bot_response"), None
#     else:
#         # stay on same step
#         if thread and step["step_id"] == "1":
#             next_step = step["next_step"]
#             thread.flow_id = flow_id
#             thread.step_id = next_step
#             thread.step_count = 1
#             thread.previous_flow=thread.flow_id
#             thread.previous_step=thread.step_id
#             await thread.save()
#         return llm_json.get("bot_response"), None
