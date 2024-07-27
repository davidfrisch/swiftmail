#! python3
import random
import os 
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tasks.dataset.bank_questions import ucl_questions
from LLM.OllamaLLM import OllamaAI
import json

def generate_fake_email(ollamaLLM, numb_questions=5):
        
    random_questions = random.sample(ucl_questions, numb_questions)
    selected_questions = [q['question'] for q in random_questions]
    print(selected_questions)
    prompt = f"""
      Your name is John Doe and you are applying for a graduate program in Software Engineering. 
      You are a {random.choice(['local', 'international'])} student that is interested in the MSc program at UCL.
      
      Write an email to UCL admissions asking the following questions:\n 
      {' \n '.join(selected_questions)}
      
    """
   
    return ollamaLLM.predict(prompt), random_questions, prompt


def generate_fake_emails(ollamaLLM, numb_emails=5, numb_questions=None):
    is_random_numb_questions = numb_questions is None
    timestamp = str(int(time.time()))
    for i in range(numb_emails):
      numb_questions = random.randint(1, 3) if is_random_numb_questions else numb_questions
      print(f"Generating fake email {i} with {numb_questions} questions ({"random" if is_random_numb_questions else "fixed"})") 
      output, questions, prompt = generate_fake_email(ollamaLLM, numb_questions)
      json_output = {
          "email": output,
          "questions": questions,
          "prompt": prompt
      }
      url_path = "../dataset"
      with open(f'{url_path}/fake_email_{i}.json', 'w') as f:
          json.dump(json_output, f)


if __name__ == '__main__':
    llm = OllamaAI('http://localhost:11434', 'llama3.1:latest')
    numb_emails = 20
    
    generate_fake_emails(llm, numb_emails)