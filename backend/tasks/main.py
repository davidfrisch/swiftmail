import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from LLM.OllamaLLM import OllamaAI
from AnythingLLM_client import AnythingLLMClient
from extract_questions import extract_questions_from_text
from answer_questions import answer_question
from generate_response_email import generate_response_email
from evaluate_answer import evaluate_answer
from constants import WORKSPACE_CATEGORIES as categories
from bank_questions import ucl_info
import random
import json

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






def main():
    llm = OllamaAI('http://localhost:11434', 'llama3:instruct')
    anything_llm_client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")

    for i in range(10):
        print(f"Generating fake email {i}")
        output, questions, prompt = generate_fake_email(llm, random.randint(1, 5))
        json_output = {
            "email": output,
            "questions": questions,
            "prompt": prompt
        }
        with open(f'fake_emails/fake_email_{i}.json', 'w') as f:
            json.dump(json_output, f)

            
    return
    
    
    with open('fake_email_2.txt', 'r') as f:
        text = f.read()
    
    questions = extract_questions_from_text(llm, text)
    print(questions)
    for question in questions:
        category = question['category']
        if category not in categories:
            print(f"Category {category} not found in categories")
            category = "general"
        
        question_text = question['question'] + "\n  In your answer put in ** all qualitative information (words, date, numbers, time)"
        answer = answer_question(anything_llm_client, question_text, category)
        print(answer)
        question['answer'] = answer
        
    # response_email = generate_response_email(llm, text, questions)
    # print(response_email)
    

    # # with open('responses.json', 'r') as f:
    # #     questions = json.load(f)
    
    # for question in questions:
    #   category = question['category']
    #   question_text = question['question']
    #   answer = question['answer']
    #   evaluation = evaluate_answer(llm, question_text, answer)
    #   question['evaluation'] = evaluation
    #   print(evaluation)
        
    
    
if __name__ == '__main__':
    main()