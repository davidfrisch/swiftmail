import json
import chromadb
import ollama
import json
from typing import List, Dict, Any


def linkert_eval(model, question:str, answer: str):
    # Provide an answer to the question
    prompt = f"""
      From this question:
      Question: {question}
      Does the following answers the question?
      Answer: {answer}
      ---
      Provide in json format with a key of 'score' and a value of 0 to 5, where 
      1 means the answer cannot be answered,
      2 means the answer is not helpful and gives irrelevant information,
      3 means the answer is not helpful and gives irrelevant information and asks to do more,
      4 means the answer is helpful and gives relevant information but asks to do more,
      5 means the answer is helpful and gives relevant information without asking to do more.
      
      schema:
      {{ "score": int }}
    """
    
    result = model.predict(prompt, format="json")
    score = int(json.loads(result)['score'])
    return score


def binary_eval(model, question:str, answer: str):
    # Provide an answer to the question
    prompt = f"""
      From this question:
      Question: {question}
      Does the following answer answer the question?
      Answer: {answer}
      
      Provide in a json format with a key of 'score' and a value of 0 or 1, where 0 means the answer is not helpful and 1 means the answer is helpful and gives relevant information without asking to do more.
    """
    result = model.predict(prompt, format="json")
    res = json.loads(result)['score']
    return int(res)


def hallucination_eval(model, draft_email,  sources):
    retrieve_text = [source["text"].split("</document_metadata>\n\n")[1] for source in sources]
    retrieve_text = "\n".join(retrieve_text)
    retrieve_text = retrieve_text.replace("\xa0", "\n")
    
    
    prompt = f"""
      Is the following reply email only based on the context?
      -Beginning of the context--
      Context: {retrieve_text}
      -End of the context--
      ----
      Email: {draft_email}
      ---
    
      reply in json format with a key of 'hallucination' and a value of 0 or 1, where 0 means the answer is based on the context and 1 means the answer is not based on the context.
      
      schema: 
      {{ "hallucination": int }}
    """
    
    result = model.predict(prompt, format="json")
    res = json.loads(result)['hallucination']
    return int(res)
  




def answer_eval(model, question:str, answer: str, sources):
    bin_score = binary_eval(model, question, answer)
    linkert_score = linkert_eval(model, question, answer)
    hallucination_score = hallucination_eval(model, answer, sources)
    
    return {
      'binary' : bin_score,
      'linkert' : linkert_score,
      'hallucination' : hallucination_score
    }


def binary_eval_draft_email(model, draft_email: str):
    prompt = f"""
      Is the following reply email helpful and gives relevant information without asking to do more?
      Email: \n {draft_email}
      ---
      Provide in a json format with a key of 'score' and a value of 0 or 1, where 0 means the answer is not helpful and 1 means the answer is helpful and gives relevant information without asking to do more.
    """

    result = model.predict(prompt, format="json")
    res = json.loads(result)['score']
    return int(res)
  
def linkert_eval_draft_email(model, draft_email: str):
    prompt = f"""
      From this email:
      Email: {draft_email}
      ---
      Provide in json format with a key of 'score' and a value of 0 to 5, where 
      1 means the answer cannot be answered,
      2 means the answer is not helpful and gives irrelevant information,
      3 means the answer is not helpful and gives irrelevant information and asks to do more,
      4 means the answer is helpful and gives relevant information but asks to do more,
      5 means the answer is helpful and gives relevant information without asking to do more.
    """
    
    result = model.predict(prompt, format="json")
    score = int(json.loads(result)['score'])
    return score

def draft_email_eval(model, draft_email, sources):
    bin_score = binary_eval_draft_email(model, draft_email)
    linkert_score = linkert_eval_draft_email(model, draft_email)
    hallucination_score = hallucination_eval(model, draft_email, sources)
    
    return {
      'binary' : bin_score,
      'linkert' : linkert_score,
      'hallucination' : hallucination_score
    }