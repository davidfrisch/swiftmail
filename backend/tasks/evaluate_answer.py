import json
import chromadb
import ollama
import json
from typing import List, Dict, Any


def score_answer(model, question:str, answer: str):
    # Provide an answer to the question
    prompt = f"""
      From this question:
      Question: {question}
      Does the following answers the question?
      Answer: {answer}
      ---
      Provide in json format with a key of 'score' and a value of 0 to 10, where 0 means the answer is not helpful and 10 means the answer is helpful and gives relevant information without asking to do more.
    """
    
    result = model.predict(prompt, format="json")
    score = int(json.loads(result)['score'])
    return score


def binary_score_answer(model, question:str, answer: str):
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


def evaluate_answer_with_chromadb(model, question:str, answer: str):
    # Does not work well
    client = chromadb.PersistentClient(path="../../chromadb/chroma")
    collection = client.get_collection(name="general")

    num_results = 2

    response = ollama.embeddings(
      prompt=answer,
      model="nomic-embed-text"
    )

    results = collection.query(
      query_embeddings=[response["embedding"]],
      n_results=num_results,
    )
    
    data: List[Dict[str, Any]] = [
      { 'id' : id, 'distance' : distance, 'text' : text, 'metadata' : metadata }
      for id, distance, text, metadata in zip(results['ids'][0], results['distances'][0], results['documents'][0], results['metadatas'][0])
    ]

    documents = [doc['text'] for doc in data]
    prompt = f"""
    What informations is incorrect in the answer given the faq ? 
    answer: {answer}
    ---
    context: {'\n'.join(documents)}
    ---
    Reply in a json with informations key and a list of informations that are not in the context.
    """
   
    result = model.predict(prompt, format="json")
    result = json.loads(result)
    informations = result['informations']
    return {
      'number_of_information' : len(informations),
      'informations' : informations
    }
  




def evaluate_answer(model, question:str, answer: str):
    bin_score = binary_score_answer(model, question, answer)
    score = score_answer(model, question, answer)
    eval_score = evaluate_answer_with_chromadb(model, question, answer)
    return {
      'binary_score' : bin_score,
      'score' : score,
      'eval_score' : eval_score
    }