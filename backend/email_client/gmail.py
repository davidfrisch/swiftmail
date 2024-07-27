from simplegmail import Gmail
from simplegmail.query import construct_query

import os 
import sys
import time
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import LLM.OllamaLLM as OllamaLLM
gmail = Gmail()
ollama_client = OllamaLLM.OllamaAI('http://localhost:11434', 'gemma:2b')



def get_unread_emails(query_params: dict):
    query = construct_query(query_params)
    messages = gmail.get_unread_inbox(query=query)
    return messages
 
 

def filter_university_enquiries(messages):
    enquiries = []
    for message in messages:
        prompt = f"""
          Is this email ask at least one question about program at UCL (university)?:
          
          Subject:
          {message.subject}
          -
          Body: 
          {message.plain[:500] if message.plain else ""}
          
          ---
          expected output is a JSON object with the following structure:
          {{
            "is_university_enquiry": boolean,
          }}
        """
        
        raw_response = ollama_client.predict(prompt, format="json")
        try:
            response = json.loads(raw_response)
            if response['is_university_enquiry']:
                enquiries.append(message)
        except Exception as e:
            print("Error parsing response")
            print(e)
            print(raw_response)
            print("-------")
            
    return enquiries
 
 
def get_unread_enquiries():
    query_params = {
        "newer_than": (1, "year"),
    }
    messages = get_unread_emails(query_params)
    enquiries = filter_university_enquiries(messages)
    return enquiries