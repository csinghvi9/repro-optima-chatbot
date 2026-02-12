from app.core.boto3client import bot_generate
import json
from app.models.threads import Thread
from bson import ObjectId
import ast


async def greetingsFlow(user_message, language: str, thread_id: str):

    # Explicitly keep messages as a list of separate strings
    messages = "Hello 👋 I’m here to help you with all your queries and tasks"
    another_message = "I am Fine How can I help you today!"
    thanks_message = "Hope this was helpful. Let me know if you need more info"
    help_message = "How can I help you?"

    prompt = f"""
You are a helpful assistant.

User message: {user_message}

Instructions:
1. Detect the intent of the user's message and the user question can be in Hinglish also undestand that.
2. Choose ONLY ONE of the following three responses:
   - Greeting response in any language → "{messages}"
   - Well-being response → "{another_message}"
   - Thanks response → "{thanks_message}"
   -Help/assist/guide/uphold/encourage etc if the user wants help from the bot-> "{help_message}"
3. Translate the selected response COMPLETELY into the target language: {language}.
4. The response must always be written in a warm, polite, and friendly female tone.
5. Output ONLY the translated text — NO explanations, NO extra words like "translated in", "here is", ":", etc.
6. The output must be a single plain string (the translated version of one of the three above messages).
7. Do NOT mix languages. The response must be entirely in {language}.
8. Do NOT create or modify any response beyond the three defined above.
9. Do NOT add punctuation or text not in the original message.
10. Always answer in a woman tone

Output format:
Just the translated message (nothing else).
"""

    answer = await bot_generate(prompt, 200)

    try:
        answer = json.loads(answer)  # will give list
    except:
        try:
            answer = ast.literal_eval(answer)
        except Exception:
            answer = [answer]

    thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
    if thread:
        thread.flow_id = None
        thread.step_id = None
        thread.previous_flow = "greetings"
        thread.previous_step = thread.step_id
        await thread.save()
    return answer
