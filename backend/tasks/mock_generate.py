import random
import os 
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from bank_questions import ucl_info

def generate_fake_email(ollamaLLM, numb_questions=5):
    all_questions = []
    for _, questions in ucl_info.items():
        all_questions.extend(questions)
        
    random_questions = random.sample(all_questions, numb_questions)
    prompt = f"""
      Your name is John Doe and you are applying for a graduate program in Software Engineering. 
      You are a {random.choice(['local', 'international'])} student that is interested in the program at UCL.
      
      Write an email to UCL admissions asking the following questions:\n 
      {' \n '.join(random_questions)}
      
    """
   
    return ollamaLLM.predict(prompt), random_questions, prompt


def generate_fake_emails(ollamaLLM, numb_emails=5, numb_questions=5):
    timestamp = str(int(time.time()))
    for i in range(numb_emails):
      print(f"Generating fake email {i}")
      output, questions, prompt = generate_fake_email(ollamaLLM, numb_questions)
      json_output = {
          "email": output,
          "questions": questions,
          "prompt": prompt
      }
      with open(f'fake_emails/fake_email_{i}_{timestamp}.json', 'w') as f:
          json.dump(json_output, f)
