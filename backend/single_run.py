#!/usr/bin/env python

import os 
import sys
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from LLM.OllamaLLM import OllamaAI
from LLM.AnythingLLM_client import AnythingLLMClient
from Generater import Generater
from Reviewer import Reviewer
import json


def main(email_body: str, with_interaction: bool):
    ollama_client = OllamaAI('http://localhost:11434', 'llama3:instruct')
    anything_llm_client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")
    output_path = '../outputs/response.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    generater = Generater(ollama_client=ollama_client, anyllm_client=anything_llm_client)
    generater.reply_to_email(email_body, output_path, with_interaction)
    
    evaluator = Reviewer(ollama_client, output_path)
    evaluator.evaluate()
        
    
    

def arg_parser():
    parser = argparse.ArgumentParser(prog="main.py", description="Process email body and generate response")
    parser.add_argument('-w', action='store_true', help="Whether to interact with the user to improve the answer", default=False)
    args = parser.parse_args()
    return args     
    
    
if __name__ == '__main__':
    
    args = arg_parser()
    
    
    with open('../dataset/fake_email_1.json', 'r') as f:
      fake_email = json.load(f)
    
    email_body = fake_email['email']
        
    main(email_body, args.w)
    