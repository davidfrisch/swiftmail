#!/usr/bin/env python

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
import json



def generate(llms, text):
    ollama_client = llms['ollama']
    anything_llm_client = llms['anything_llm']
    questions = extract_questions_from_text(ollama_client, text)
    print(questions)
    
    for question in questions:
        category = "General" # question['category']
        question['additional_context'] = ""
        summary = question['summary']
        
        if category not in categories:
            print(f"Category {category} not found in categories")
            category = "General"
        
        tries = 0
        while tries < 3:
            question_text = question['question'] + "--- \n Additional context: "+ question['additional_context'] +" \n --- \n  In your answer put in ** all qualitative information (words, date, numbers, time)" 
            has_additional_context = True if question['additional_context'] != "" else False
            
            answer, unique_chunk_sources, total_sim_distance = answer_question(anything_llm_client, question_text, summary, category, has_additional_context)
            print("Question: ", question_text)
            print("Answer: \n ", answer)
            print("Unique chunk sources: ", unique_chunk_sources)
            print("Total sim distance: ", total_sim_distance)
            print(f"Are you satisfied with the answer? tries: {tries}")
            response = input()
            if response.strip() in ['yes', 'Yes', 'YES', 'y', 'Y']:
                break
            else:
                tries += 1
                question['additional_context'] = question['additional_context'] + "\n" + response
        
        question['answer'] = answer
      
    response_email = generate_response_email(ollama_client, text, questions)
    
    return {
        'response_email': response_email,
        'questions': questions
    }



def evaluate(llms, questions):
    # with open('responses.json', 'r') as f:
    #     questions = json.load(f)
    
    ollama_client = llms['ollama']
    for question in questions:
      category = question['category']
      question_text = question['question']
      answer = question['answer']
      evaluation = evaluate_answer(ollama_client, question_text, answer)
      question['evaluation'] = evaluation
      print(evaluation)




def main(email_body: str):
    llm = OllamaAI('http://localhost:11434', 'llama3:instruct')
    anything_llm_client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")
    llms = {
        'ollama': llm,
        'anything_llm': anything_llm_client
    }

    response = generate(llms, email_body)
    
    with open('./outputs/response.json', 'w') as f:
        json.dump(response, f)
    
    

        
    
    
if __name__ == '__main__':
    with open('./dataset/fake_email_1.json', 'r') as f:
      fake_email = json.load(f)
    
    email_body = fake_email['email']
    main(email_body)