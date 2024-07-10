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
      Does the following answer answer the question?
      Answer: {answer}
      
      Provide a score from 0 to 10, where 0 means the answer is completely wrong and 10 means the answer is answered completely and effectively.
      Answer should be like:
      '
      score : 5
      '
    """
    
    res = model.predict(prompt)
    return res

def evaluate_answer_with_chromadb(model, question:str, answer: str):
    client = chromadb.PersistentClient(path="../../chromadb/chroma")
    collection = client.get_collection(name="verifier")

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
    How many information is given in the answer that you cannot find in the given data:
    question: {question}
    \n
    answer: {answer}
    ---
    data: {'\n'.join(documents)}
    ---
    output should be like:
    number_of_information: 2
    the information that is not in the data:
    - information 1
    - information 2
    """

    result = model.predict(prompt)
    print(result)
  

def highlight_data_in_answer(model, answer: str):
    prompt = f"""
      Highlight relevant data in the following answer:
      Answer: {answer}
    """
    
    res = model.predict(prompt)
    print(res)
    


def evaluate_answer(model, question:str, answer: str):
    highlight_data_in_answer(model, answer)
    return None