#! python3
import random
import os 
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from dataset.bank_questions import ucl_questions, ucl_questions_undergrad
from backend.LLM.OllamaLLM import OllamaAI
import json

def generate_fake_email(questions_dataset, ollamaLLM, numb_questions=5):
    
    print(f"Generating fake email with {numb_questions} questions")
    random_questions = random.sample(questions_dataset, numb_questions)
    selected_questions = [q['question'] for q in random_questions]
    print(selected_questions)
    name = "Lewis Smith"
    level_of_study = "undergraduate"
    program = "Computer Science"
    prompt = f"""
      Your name is {name} and you are applying for a {level_of_study} program in {program} at UCL.
      You are a {random.choice(['local', 'international'])} student that is interested in the program.
      
      Write an email to UCL admissions asking the following questions:\n 
      {' \n '.join(selected_questions)}
      
    """
   
    return ollamaLLM.predict(prompt), random_questions, prompt


def generate_fake_emails(ollamaLLM, questions_dataset, numb_emails=5, numb_questions=None):
    is_random_numb_questions = numb_questions is None
    timestamp = str(int(time.time()))
    for i in range(numb_emails):
      numb_questions = random.randint(1, 3) if is_random_numb_questions else numb_questions
      print(f"Generating fake email {i} with {numb_questions} questions ({"random" if is_random_numb_questions else "fixed"})") 
      output, questions, prompt = generate_fake_email(questions_dataset, ollamaLLM, numb_questions)
      json_output = {
          "email": output,
          "questions": questions,
          "prompt": prompt
      }
      url_path = "../dataset"
      with open(f'{url_path}/fake_email_undergrad_{i}.json', 'w') as f:
          json.dump(json_output, f)


if __name__ == '__main__':
    llm = OllamaAI('http://localhost:11434', 'llama3.1:latest')
    numb_emails = 20
    
    generate_fake_emails(llm, ucl_questions_undergrad, numb_emails)