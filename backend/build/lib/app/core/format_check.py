from app.utils.llm_utils import ask_openai_validation_assistant
import json
import ast


async def on_validation_failure(language):
    if language == "English":
        llm_answer = {
            "first_text": "For more specific information, please connect with our call center between 9 AM and 6 PM.",
            "second_text": "CUSTOMER CARE NUMBER",
            "phone_number": "+6332-256-2433",
        }
    else:
        prompt = f"""You are a translation assistant.
            Always return the response only as a Python-style dictionary in the exact same format and with the exact same keys as shown below.
            Do not translate, modify, rename, reorder, add, or remove any keys .
            Do not change the dictionary structure or formatting.
            Translate only the values of "first_text" and "second_text" into the language-{language}.
            Do not translate the phone number.
            If a language is provided, translate accurately and naturally into that language-{language}.
            Output must strictly be this dictionary and nothing else.
            Base format (keys must remain unchanged):
            {{"first_text": "For more specific information, please connect with our call center between 9 AM and 6 PM.",
              "second_text": "CUSTOMER CARE NUMBER",
              "phone_number": "+6332-256-2433"}}"""
        llm_answer = await ask_openai_validation_assistant(prompt)
        try:
            llm_answer = json.loads(llm_answer)
        except Exception:
            try:
                llm_answer = ast.literal_eval(llm_answer)
            except Exception:
                llm_answer = {
                    "first_text": "For more specific information, please connect with our call center between 9 AM and 6 PM.",
                    "second_text": "CUSTOMER CARE NUMBER",
                    "phone_number": "+6332-256-2433",
                }
    return False, llm_answer


async def validate_answer(answer, expected_format, language):

    # Type check
    if type(answer) != type(expected_format):
        return await on_validation_failure(language)

    # String
    if isinstance(expected_format, str):
        return True, ""

    # List
    if isinstance(expected_format, list):
        if len(answer) != len(expected_format):
            return await on_validation_failure(language)

        for i, (ans_item, fmt_item) in enumerate(zip(answer, expected_format)):
            valid, msg = await validate_answer(ans_item, fmt_item, language)
            if not valid:
                return await on_validation_failure(language)

        return True, ""

    # Dict
    if isinstance(expected_format, dict):
        if set(answer.keys()) != set(expected_format.keys()):
            return await on_validation_failure(language)

        for key in expected_format:
            valid, msg = await validate_answer(
                answer[key], expected_format[key], language
            )
            if not valid:
                return await on_validation_failure(language)

        return True, ""

    return await on_validation_failure(language)
