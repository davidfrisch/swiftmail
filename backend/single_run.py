#!/usr/bin/env python

import os 
import sys
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from LLM.OllamaLLM import OllamaAI
from LLM.AnythingLLM_client import AnythingLLMClient
from Generater import Generater
from Reviewer import Reviewer
from database import schemas
import json


def main(email: schemas.Email):
    ollama_client = OllamaAI('http://localhost:11434', 'llama3:instruct')
    anything_llm_client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")
    output_path = '../outputs/response.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    generater = Generater(ollama_client=ollama_client, anyllm_client=anything_llm_client)
    
    generater.single_run_reply_to_email(email, output_path)
    
    # evaluator = Reviewer(ollama_client, output_path)
    # evaluator.evaluate()
        
    
    

    
if __name__ == '__main__':
    
    with open('../dataset/fake_email_3.json', 'r') as f:
      fake_email = json.load(f)
    
    email_body = fake_email['email']
    subject = fake_email['email'].split('\n\n')[0]
    new_email = schemas.Email(
        body=email_body, 
        subject=subject,
        sent_at="2022-01-01",
        id=-1,
        is_read=False,
    )
    main(new_email)
    
