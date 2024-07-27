from simplegmail import Gmail
from simplegmail.query import construct_query
import os 
import sys
import time
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import backend.LLM.OllamaLLM as OllamaLLM
gmail = Gmail()

query_params = {
    "newer_than": (1, "year"),
}

llm = OllamaLLM.OllamaAI('http://localhost:11434', 'gemma:2b')
messages = gmail.get_unread_inbox()
print(f"Found {len(messages)} unread messages")
start_time = time.time()
for message in messages:
    print("Subject: " + message.subject)
    
    prompt = f"""
      Is this email ask at least one question about program at UCL (university)?:
      
      Subject:
      {message.subject}
      -
      Body: 
      {message.plain[:500]}
      
      ---
      expected output is a JSON object with the following structure:
      {{
        "is_university_enquiry": boolean,
      }}
    """
    
    raw_response = llm.predict(prompt, format="json")
    try:
        response = json.loads(raw_response)
        print(response)
        print("-------")
    except Exception as e:
        print("Error parsing response")
        print(e)
        print(raw_response)
        print("-------")
        
end_time = time.time()
print(f"Processed {len(messages)} emails in {end_time - start_time} seconds")