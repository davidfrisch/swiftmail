import json


def evaluate_answer(model, question:str, answer: str):
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
    print(res)