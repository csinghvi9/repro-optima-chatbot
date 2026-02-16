# from langchain.prompts import PromptTemplate
# from langchain.chains.retrieval import create_retrieval_chain
# from langchain_openai import ChatOpenAI
# from app.core.kbSetUP import get_vectorstore
# from app.utils.config import ENV_PROJECT


# async def FAQFlow(user_message: str, language: str):

#     vectorstore = get_vectorstore()
#     custom_prompt = PromptTemplate(
#         template="""
# You are a helpful IVF assistant. Use the following context to answer the question.

# Instructions:
# - Preserve the grammatical style and phrasing of the knowledge base.
# - Summarize your answer in 10-50 words.
# - Answer in the following language: {language}

# Context:
# {context}

# Question:
# {question}

# Answer:""",
#         input_variables=["context", "question", "language"]
#     )

#     llm = ChatOpenAI(model="gpt-4.1-nano",openai_api_key=ENV_PROJECT.OPENAI_API_KEY)

#     qa_chain = RetrievalQAWithSourcesChain(
#         llm=llm,
#         retriever=vectorstore.as_retriever(),
#         chain_type="stuff",
#         chain_type_kwargs={"prompt": custom_prompt}
#     )

#     response = qa_chain.run({"question": user_message, "language": language})
#     return response
# from langchain.prompts import PromptTemplate
# from langchain.chains.retrieval import create_retrieval_chain
# from langchain_openai import ChatOpenAI
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from app.core.kbSetUP import get_vectorstore
# from app.utils.config import ENV_PROJECT
# import json


# async def FAQFlow(user_message: str, language: str):
#     print("in faq flow")
#     # Get vectorstore retriever
#     vectorstore = get_vectorstore()
#     retriever = vectorstore.as_retriever()
#     messages = ["I understand your query, but is there any anything else you want to know",
#             {"first_text":"For more specific information, please connect with our call center between 9 AM and 6 PM.","second_text":"CUSTOMER CARE NUMBER","phone_number":"1800 3092429"},
#             "Hope this helps! You can come back anytime to explore  or get more info"
#         ]

#     # Define custom prompt
#     custom_prompt = PromptTemplate(
#     template="""
# You are a helpful IVF assistant. Use the following context to answer the question.

# Instructions:
# - Preserve the grammatical style and phrasing of the knowledge base.
# - Summarize your answer in 10-50 words.
# - Answer in the following language: {language}
# - if you don't find the answer then return {another_message} in the same structure with translated language not the number

# Context:
# {context}

# Question:
# {input}

# Answer:(as JSON): """,
#     input_variables=["context", "input", "language","another_message"]
# )

#     # Initialize LLM
#     llm = ChatOpenAI(
#         model="gpt-4.1-nano",
#         openai_api_key=ENV_PROJECT.OPENAI_API_KEY
#     )

#     # Step 1: Create a document-combining chain (stuff = simple concatenation)
#     combine_docs_chain = create_stuff_documents_chain(
#         llm=llm,
#         prompt=custom_prompt
#     )

#     # Step 2: Create retrieval chain
#     qa_chain = create_retrieval_chain(
#     retriever=retriever,
#     combine_docs_chain=combine_docs_chain
# )

#     # Run the chain
#     response = await qa_chain.ainvoke({
#         "input": user_message,
#         "language": language,
#         "another_message":messages
#     })
#     try:
#         answer_list = json.loads(response["answer"])
#     except:
#         answer_list=[response["answer"]]
#     print(answer_list)

#     return answer_list


# async def query_vectorstore(query: str, k: int = 3):
#     vs = get_vectorstore()
#     results = vs.similarity_search(query, k=k)
#     if not results:
#         return None
#     return results

from app.core.boto3client import bot_generate
from app.core.kbSetUP import get_vectorstore, get_docs
import ast
from langchain_openai import OpenAIEmbeddings
from app.utils.config import ENV_PROJECT
import json
from app.models.threads import Thread
from bson import ObjectId


async def FAQFlow(user_message: str, language: str, thread_id: str, context=None):
    if not (context):
        context = await query_vectorstore(user_message, language)
    thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
    messages = "Sorry I'm unable to understand your query. Please let me know if I can help you with IVF or related treatment queries."

    if isinstance(context, list):
        seen = set()
        unique_docs = []
        for doc in context:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_docs.append(doc.page_content)
        context_text = " ".join(unique_docs)
    else:
        context_text = context
    prompt = f"""
You are a helpful IVF assistant. Use the following context to answer the question.

Context:-{context_text}

Instructions:
Step 1: Translate the question into English.
Step 2: Determine if the context answers the user's question. Do NOT rely on exact words—if the meaning is the same, it is relevant. 
Check synonyms, different phrasing, and implied meaning.ChatGPT said:

If the user message is a short single sentence like “why,” “what,” or “hello” and not related to IVF, fertility, or medical topics, return status-irrelevant. 
***VERYVER IMPORTANT Step***
-****but if the question asked by the user is same as the question in the text then return as it is and status as relevant 
-the context and the question words or language may be different but if their meaning is same then it is relevant
- If the context is even partially relevant, you MUST generate the answer ONLY from the context and return status as relevant.
- Summarize your answer in 10-50 words.
- Preserve the grammatical style and phrasing of the knowledge base.
- Answer in the following language: {language} only.**most important**- answer should always be in this given language only even if there is any chip name in the response translate that also
-**Even if there are chip names, feature names, button names, hospitals, flows, actions, or model functions — translate all of them fully into {language} like for eg “Find Hospital” as "अस्पताल खोजें".
- Do NOT mention or imply that the context is being used.
- Do NOT say things like “the context mentions”, “it is not specified”, or “the context does not provide” or 'The context indicates that there' etc.
-If the user is asking about specific doctor or name of the doctor (only doctor name nothing else) and the context does not mention the doctor name then do not give the this text "the context does not mention or specify" or anything about context in answer
-In answer do not give anything like which gives that answer is coming from context
- Just provide a smooth, complete, and natural answer as if you are directly answering the user.

Strict Rule:
- If the context is relevant → ONLY answer from the context->return json
- If the context is NOT relevant or does not provide information at all → return bot_response this string exactly , ***translate the message into :{language} but don't translate the key of the dictionary
-and do not give relevant or irrelavant in bot response only in status and the bot_response thing should only contains the response
-return the response translated only in this langauge{language} and for dict response do not translate the keys
-if the status is relevant then only there should be a bot response otherwise it should be an empty string

IMP***-The response must always be written in a warm, polite, and friendly female tone.


Do not merge both. Return ONLY one of the two:
1. Answer (based on context)
2. Or the invalid message JSON
3.This is important
4.Return as valid json for all language do not add any "\n" and the bot response should be in double quotes irrespective in any language

Question:
{user_message}


Ouput Format:
{{
  "status": "Relevant" or "Irelevant",
  "bot_response": Answer (as string)
}}
"""

    answer = await bot_generate(prompt, 500)
    try:
        answer = json.loads(answer)
    except Exception:
        # fallback if model doesn't output strict JSON
        try:
            answer = ast.literal_eval(answer)
        except Exception:
            answer = {"status": "Irelevant"}
    if answer["status"] == "Relevant":
        try:
            # Try evaluating the string to an actual list
            answer = ast.literal_eval(
                answer["bot_response"]
            )  # Safely evaluate the string to a list
        except (ValueError, SyntaxError) as e:
            answer = [answer["bot_response"]]

        if thread:
            thread.flow_id = None
            thread.step_id = None
            thread.previous_flow = "faq_flow"
            thread.previous_step = thread.step_id
            await thread.save()
        return answer, True
    else:
        if language != "English":
            prompt = f"translate this message-{messages} into {language} and don not add anything extra from your side just translate and return the do not give Output-or any such thing like this only pure message translated in that language  Output:string"
            llm_answer = await bot_generate(prompt, 400)

            if thread:
                thread.flow_id = None
                thread.step_id = None
                thread.previous_flow = "faq_flow"
                thread.previous_step = thread.step_id
                await thread.save()

            # ✅ handle both possible structures
            if isinstance(llm_answer, dict):
                return llm_answer.get("bot_response", llm_answer), False
            elif isinstance(llm_answer, list):
                return llm_answer, False
            elif isinstance(llm_answer, str):
                return llm_answer, False
            else:
                return messages, False
        if thread:
            thread.flow_id = None
            thread.step_id = None
            thread.previous_flow = "faq_flow"
            thread.previous_step = thread.step_id
            await thread.save()
        return messages, False


from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever


def build_ensemble_retriever(vectorstore, docs):
    # Dense retriever (semantic)
    dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

    # Sparse retriever (keyword)
    sparse_retriever = BM25Retriever.from_documents(docs)

    # Combine both for better context
    ensemble = EnsembleRetriever(
        retrievers=[dense_retriever, sparse_retriever],
        weights=[0.6, 0.4],  # tune weights if needed
    )

    return ensemble


# Optional helper function
async def query_vectorstore(query: str, language: str, k: int = 5):
    vs = get_vectorstore()
    docs = get_docs()

    if language.lower() != "english":
        prompt = f"""
        You are a translation engine. Translate the text inside quotes into English only.
        "{query}"
        """
        query = await bot_generate(prompt, 100)

    ensemble = build_ensemble_retriever(vs, docs)
    results = ensemble.get_relevant_documents(query)

    if not results:
        return None

    return results
