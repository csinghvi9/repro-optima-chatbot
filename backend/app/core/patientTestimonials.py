from app.utils.llm_utils import ask_openai_validation_assistant
import json, ast


async def patientTestimonialsSorryMessage(language):
    messages = [
        "Sorry, I am unable to help you with this query currently. Please let me know if there's anything related to IVF which I can help you with.",
        {
            "first_text": "For more specific information, please connect with our call center between 9 AM and 6 PM.",
            "second_text": "CUSTOMER CARE NUMBER",
            "phone_number": "18003092323",
        },
        "Hope this helps!\n You can revisit us anytime for more information.",
    ]
    if language != "English":
        prompt = f"""
                    Translate the following content into {language}.

                    Rules:
                    - Return ONLY the translated output.
                    - Preserve the exact data structure (a Python list with strings and a dictionary).
                    - DO NOT translate dictionary keys: first_text, second_text, phone_number.
                    - DO NOT modify numbers, punctuation, line breaks, or formatting.
                    - Translate only the string values.
                    - Do NOT add explanations, comments, or extra text.

                    Input:
                    {messages}

                    Output:
                    """
        answer = await ask_openai_validation_assistant(prompt)
        try:
            llm_json = json.loads(answer)
        except Exception:
            # fallback if model doesn't output strict JSON
            try:
                llm_json = ast.literal_eval(answer)
            except:
                llm_json = [messages]
        return llm_json
    return messages
