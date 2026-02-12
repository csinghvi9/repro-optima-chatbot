from app.core.boto3client import bot_generate
import json
from app.models.threads import Thread
from bson import ObjectId
import ast
import traceback
import re
from app.core.format_check import validate_answer


async def parse_answer(raw):
    if not raw:
        return []

    if isinstance(raw, list):
        return raw

    raw = raw.strip()

    # 1️⃣ Try clean JSON
    try:
        return json.loads(raw)
    except Exception:
        pass

    # 2️⃣ Try to detect wrapped JSON array string
    # Example: "['[\n  \"text1\", ... ]']"
    try:
        if raw.startswith("['[") and raw.endswith("]']"):
            inner = raw[2:-2]  # unwrap
            inner = inner.encode("utf-8").decode("unicode_escape")
            return json.loads(inner)
    except Exception:
        pass

    # 3️⃣ Try to extract JSON array inside raw text
    try:
        match = re.search(r"(\[.*\])", raw, flags=re.DOTALL)
        if match:
            candidate = match.group(1)
            candidate = candidate.replace("\n", "")
            candidate = re.sub(r"\s+", " ", candidate).strip()
            return json.loads(candidate)
    except Exception:
        pass

    # 4️⃣ Try single quotes → double quotes normalization
    try:
        cleaned = re.sub(r"(?<!\\)'", '"', raw)
        cleaned = re.sub(r",(\s*[\]}])", r"\1", cleaned)
        return json.loads(cleaned)
    except Exception:
        pass

    # 5️⃣ Final fallback: literal eval
    try:
        val = ast.literal_eval(raw)
        if isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return [val]
        return val
    except Exception:
        traceback.print_exc()
        return [raw]


async def loan_emi_option(user_message, language: str, thread_id: str):

    # Explicitly keep messages as a list of separate strings
    messages = [
        "At Indira IVF, we offer 0% interest EMI and loan facilities for IVF treatment. If you are eligible, you can avail of these options to ease the financial burden.",
        "We suggest you first visit the center for a consultation. The doctor will explain the treatment process and give you an estimate of the total cost. After that, you can speak to our loan department, and they will guide you through the entire loan process and provide all necessary details.",
        "To check your eligibility or know more simply click on button given below",
        {"content": "Bringing your parenthood dream closer"},
    ]

    prompt = f"""
You are a helpful assistant.
user message = {user_message}

Rules (apply in order, highest priority first):

1. If the user provides incorrect, irrelevant, misleading, accusatory, or hostile statements about IVF loans/EMIs
   OR expresses blame, complaint, or suspicion about IVF loans/EMIs,
   → Then return exactly:
   ["I can't help you on this. Is there anything else I can do?"]

   **** IMP_NOTE****: Statements showing financial difficulty such as
   "I cannot afford IVF", "IVF is too costly for me", 
   or "I don't have enough money for IVF"
   should NOT be considered negative. They go to Rule 2.

2. If the user shows genuine informational intent about IVF loan or EMI options,
   OR expresses financial inability to afford IVF costs,
   → Then translate EACH input message into {language}.
   -> Return the same number of items as in {messages}.
   -> Dict keys must not be translated. Only values translated.
   -> ****VERY IMP ****- And the structure of the response and the messages in the response  should be same do not add anything in message or merge response on your own give three string and one dict translated in {language}
    ->response structure string1 -0% intrest string then string2- visit our center and string3- click button 

3. If the user message is not about loan/EMI at all,
   → Return exactly:
   "I can't help you on this. Is there anything else I can do?"

Output: valid JSON.

Output Format Example:
["<translated message 1>", "<translated message 2>", "<translated message 3>", {{ "content": "<translated content>" }}]

If invalid then return exactly:
"I can't help you on this. Is there anything else I can do?"

Important:
- Output must be valid JSON (UTF-8).
- Never use single quotes (') around any word inside the messages.
- Always use double quotes (") only for JSON structure, not for natural language emphasis.
"""

    answer = await bot_generate(prompt, 1000)

    answer = await parse_answer(answer)

    if isinstance(answer, list) and len(answer) > 1:
        is_validated, response = await validate_answer(answer, messages, language)
        if not (is_validated):
            return response, "out_of_context"
    else:
        is_validated, response = await validate_answer(
            answer,
            "I can't help you on this. Is there anything else I can do?",
            language,
        )
        if not (is_validated):
            return response, "out_of_context"

    thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
    if thread:
        thread.flow_id = None
        thread.step_id = None
        thread.previous_flow = "loan_and_emi"
        thread.previous_step = thread.step_id
        await thread.save()
    return answer, None
