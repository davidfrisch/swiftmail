#!/usr/bin/env python

import os 
import sys
import time
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from LLM.OllamaLLM import OllamaAI
from AnythingLLM_client import AnythingLLMClient
from extract_questions import extract_questions_from_text
from answer_questions import answer_question
from generate_response_email import generate_response_email
from evaluate_answer import answer_eval, draft_email_eval
from constants import WORKSPACE_CATEGORIES as categories
import json



def generate(llms, text, with_interaction):
    start_time = time.time()
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
        
        if not with_interaction:
            question_text = question['question'] + "--- \n Additional context: "+ question['additional_context'] +" \n --- \n  In your answer put in ** all qualitative information (words, date, numbers, time)" 
            answer, sources, total_sim_distance = answer_question(anything_llm_client, question_text, summary, category, False)
            
        else:
            tries = 0
            while tries < 3:
                question_text = question['question'] + "--- \n Additional context: "+ question['additional_context'] +" \n --- \n  In your answer put in ** all qualitative information (words, date, numbers, time)" 
                has_additional_context = True if question['additional_context'] != "" else False
                
                answer, sources, total_sim_distance = answer_question(anything_llm_client, question_text, summary, category, has_additional_context)
                print("Question: ", question_text)
                print("Answer: \n ", answer)
                print("Total sim distance: ", total_sim_distance)
                print(f"Are you satisfied with the answer? tries: {tries}")
                response = input()
                if response.strip() in ['yes', 'Yes', 'YES', 'y', 'Y']:
                    break
                else:
                    tries += 1
                    question['additional_context'] = question['additional_context'] + "\n" + response
            
            
        question['sources'] = sources
        question['total_sim_distance'] = total_sim_distance
        question['answer'] = answer
      
    response_email = generate_response_email(ollama_client, text, questions)
    response['time_generate'] =  time.time() - start_time
    draft_response_to_markdown(response)
    
    
    with open('./outputs/response.json', 'w') as f:
        json.dump(response, f)
        
    
    return {
        'response_email': response_email,
        'questions': questions
    }



def evaluate(llms, source_questions):
    output = None
    
    if isinstance(source_questions, str) and os.path.exists(source_questions):
        with open(source_questions, 'r') as f:
            output = json.load(f)
    
    if output is None:
        raise ValueError("Questions not found")
    
    
    ollama_client = llms['ollama']
    questions = output['questions']
    draft_email = output['response_email']
    
    output['questions'] = []
    for question in questions:
      category = question['category']
      question_text = question['question']
      answer = question['answer']
      sources = question['sources']
      evaluation = answer_eval(ollama_client, question_text, answer, sources)
      output['questions'].append({ "question": question_text, "evaluation": evaluation})
     
      
    
    all_sources = [source for question in questions for source in question['sources']]
    draft_score = draft_email_eval(ollama_client, draft_email, all_sources)
    output['draft_email_evaluation'] = draft_score

    return output

def draft_response_to_markdown(response):
    response_email = response['response_email']
    with open('./outputs/response.md', 'w') as f:
        f.write(response_email)
    


def main(email_body: str, with_interaction: bool):
    llm = OllamaAI('http://localhost:11434', 'llama3:instruct')
    anything_llm_client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")
    llms = {
        'ollama': llm,
        'anything_llm': anything_llm_client
    }


    generate(llms, email_body, with_interaction)
    evaluate(llms, './outputs/response.json')
        
    
    

def arg_parser():
    parser = argparse.ArgumentParser(prog="main.py", description="Process email body and generate response")
    parser.add_argument('--with_iteraction', action='store_true', help="Whether to interact with the user to improve the answer", default=False)
    args = parser.parse_args()
    return args     
    
    
if __name__ == '__main__':
    
    args = arg_parser()
    
    
    with open('./dataset/fake_email_1.json', 'r') as f:
      fake_email = json.load(f)
    
    email_body = fake_email['email']
        
    main(email_body, args.with_iteraction)
    
