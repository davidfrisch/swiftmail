#! python3
import random
import os 
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from dataset.bank_questions import ucl_questions
from backend.LLM.OllamaLLM import OllamaAI


def generate_fake_email(questions_dataset, ollamaLLM, index):
    
    print(f"Generating fake email {index} questions")
    selected_questions = questions_dataset[index]
    print(selected_questions['question'])
    name = "Lewis Smith"
    level_of_study = "graduate"
    program = "Software Engineering"
    prompt = f"""
      Your name is {name} and you are applying for a {level_of_study} program in {program} at UCL.
      
      Write an email to UCL admissions asking the following questions:\n 
      {selected_questions['question']}  
    """
   
    return ollamaLLM.predict(prompt), selected_questions, prompt


def generate_fake_emails(ollamaLLM, questions_dataset, numb_emails=5, numb_questions=None):
    dataset = []
    for i in range(numb_emails):
      filename = f"faq_question_{i}.txt"
      numb_questions = 1
      # print(f"Generating fake email {i} with {numb_questions} questions ({"random" if is_random_numb_questions else "fixed"})") 
      output, select_question, _ = generate_fake_email(questions_dataset, ollamaLLM, i)
      question_text = select_question['question']
      answer_text = select_question['answer']
      json_output = {
          "q": output,
          "a": filename,
      }
      dataset.append(json_output)
      with open(filename, 'w') as f:
          f.write(question_text + "\n")
          f.write("-----------------------------\n")
          f.write(answer_text + "\n")
     
    with open("dataset.json", 'w') as f:
        f.write(json.dumps(dataset, indent=4))


if __name__ == '__main__':
    llm = OllamaAI('http://localhost:11434', 'llama3.2:latest')
    numb_emails = 29
    
    generate_fake_emails(llm, ucl_questions, numb_emails)