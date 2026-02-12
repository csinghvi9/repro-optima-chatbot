from app.core.boto3client import bot_generate
import json
from app.models.threads import Thread
from bson import ObjectId
import ast


async def MedicalTerms(user_message, language: str, thread_id):

    # Explicitly keep messages as a list of separate strings
    if language == "English":
        user_message = user_message.strip().lower()
    prompt = f"""
You are an IVF Medical Information Assistant.  
Your role is to provide clear, accurate, and patient-friendly answers about infertility treatments, IVF procedures, medical terms, and related topics.  

User Question: {user_message}  
**IMP** - Always return the response in the same language as the user: {language}  

Knowledge Source:  
Use content ONLY from https://www.indiraivf.com/ and its subpages (including https://www.indiraivf.com/blog) and if the user asks for infertility treatment like (LIT,PLI) then refer https://www.indiraivf.com/advanced-infertility-treatment and its subpages("https://www.indiraivf.com/advanced-infertility-treatment/paternal-lymphocyte-immunization-therapy-pli").  

Strict Rules (must always be followed):  
1. The answer must be between 10–50 words.  
2. Do NOT use phrases like "for more details", "learn more", "visit here", "read further", etc.  
3. **IMP** if the user message states that if you offer any  test and if you do not find any information regarding test  then return "I don't have information regarding this CUSTOMER CARE NUMBER-18003092323".
4. Do NOT include hyperlinks or markdown links in the answer.  
5. If relevant, you may mention the treatment name (e.g., "Blastocyst Culture and Embryo Transfer") but without linking.  
6. If the exact information is not found on IVF's website, say:
   "I don't have information regarding this please contact ou \n Customer Care Number-18003092323"
7. Only provide medically accurate information supported by IVF's content. Never invent.  

***VERY_IMP-RESTRICATED CASE**
1. if the user asks about gender selection or gender detection that is striclty prohibited by Indian law then return or anything if the user asks that is prohibited by indian laws then return please it is very important case:
return this message exactly translated in the language given-"No,It is strictly prohibited by Indian law. IVF strictly follows all legal and ethical guidelines and does not perform any such procedures.  The most important thing is having a healthy baby, and we are here to help you achieve that dream safely and ethically.

Example Q&A:  
Q: What is Blastocyst Culture and Embryo Transfer?  
A: Blastocyst culture allows embryos to grow for 5–6 days before transfer, improving chances of implantation by selecting healthier embryos.  
"""
    answer = await bot_generate(prompt, 500)

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
        thread.previous_flow = "medical_terms"
        thread.previous_step = thread.step_id
        await thread.save()
    return answer
