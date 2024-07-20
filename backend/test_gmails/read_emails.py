from simplegmail import Gmail
from simplegmail.query import construct_query
import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import LLM.OllamaLLM as OllamaLLM
gmail = Gmail()

query_params = {
    "newer_than": (1, "year"),
}

llm = OllamaLLM.OllamaAI('http://localhost:11434', 'llama3:instruct')
messages = gmail.get_unread_inbox()
print(messages)

for message in messages:
    print("From: " + message.sender)
    
    prompt = f"""
      Is this email an enquiry about an MSc Program at UCL ? True or False
      
      {message.subject}
      {message.snippet}
      
      ---
      
      expected output is a JSON object with the following structure:
      {{
        "is_enquiry": [true, false],
      }}
    """
    
    response = llm.predict(prompt, format="json")
    print(response)
    print("-------")