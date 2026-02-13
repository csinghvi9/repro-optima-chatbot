from app.utils.llm_utils import ask_openai_validation_assistant
import json, ast
from app.core.format_check import validate_answer


async def faqTabAnswers(language):
    messages = [
        {
            "question": "How does the IVF process work?",
            "answer": "In this process, the female egg is taken out under anaesthesia and fertilized with the husband’s sperm in the lab. The embryo formed after 3-5 days is transferred back to the uterus.",
        },
        {
            "question": "When should a couple opt for IVF treatment?",
            "answer": "The IVF procedure can be prescribed in cases where the other fertility treatments have failed, or if the chances of a successful pregnancy are higher with this method than with any other treatment.\nIf there are no contraindications, the procedure can be carried out simply at the request of the couple by considering that precise time as the right time for IVF.",
        },
        {
            "question": "What is the success rate of IVF?",
            "answer": "Success rates strongly depend on the age of the patient, their condition, medical history and the line of treatment administered.",
        },
        {
            "question": "Can I continue working during treatments ?",
            "answer": "Yes, you may choose to continue during your treatment, just like in any other pregnancy. The doctor however may suggest differently depending on the patients treatment, condition and progress.",
        },
        {
            "question": "Is the egg collection process painfull ?",
            "answer": "The procedure is not painful as it is done under light sedation. But, at times it may cause mild discomfort. At our clinic, we use mild anaesthesia administered through an IV route which relieves discomfort.",
        },
        "For any other query, please type them in the search query box below",
    ]
    if language != "English":
        prompt = f"""
                    You are a professional medical translator.

                    TASK
                    Translate the following JSON array into {language}.

                    The input array contains TWO types of items:
                    1) Objects with keys "question" and "answer" (translate ONLY the string values of those keys)
                    2) Plain strings (translate the whole string in {language})

                    HARD RULES
                    - Output ONLY a valid JSON array (use double quotes). No markdown, no extra text.
                    - Keep the same number of items and the same order as the input array.
                    - Do NOT change the JSON structure:
                    - If an item is an object, keep it an object with ONLY "question" and "answer" keys (do NOT translate the keys).
                    - If an item is a string, keep it a string.
                    - Translate EVERY string value:
                    - For objects: translate BOTH "question" and "answer" values.
                    - For strings: translate the full string.
                    - Preserve line breaks exactly: keep \\n exactly where it appears in the input.
                    - Preserve punctuation and spacing as-is.
                    - Do not add, remove, summarize, or explain anything.
                    - Keep common medical abbreviations (IVF, IUI, ICSI) as-is (do not expand them).

                    SELF-CHECK (must do before responding)
                    Verify that:
                    - Every object's "question" and "answer" are translated into {language}
                    - Every plain string item is translated into {language}
                    - Output is valid JSON and matches the input item count and order exactly

                    INPUT JSON ARRAY:
                    {messages}
                    """
        answer = await ask_openai_validation_assistant(prompt, max_tokens=2500)
        try:
            llm_json = json.loads(answer)
        except Exception:
            # fallback if model doesn't output strict JSON
            try:
                llm_json = ast.literal_eval(answer)
            except:
                llm_json = [answer]
        is_validated, answer = await validate_answer(llm_json, messages, language)
        if not (is_validated):
            return answer, "out_of_context"
        return llm_json, None
    return messages, None
