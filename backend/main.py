from AnythingLLM_client import AnythingLLM
from LLM.OllamaLLM import OllamaAI
from constants import ANYTHING_LLM_BASE_URL, ANYTHING_LLM_TOKEN, OLLAMA_API_URL
from urls import UCL_URLS

import json
WORKSPACE_NAME = "test3"

llm = AnythingLLM(base_url=ANYTHING_LLM_BASE_URL, token=ANYTHING_LLM_TOKEN)

# llm.add_url_to_local_files(WORKSPACE_NAME, "https://www.ucl.ac.uk/students/fees/pay-your-fees/how-to-pay")
llm.create_local_folder("web-links")
llm.add_url_to_workspace(WORKSPACE_NAME, "https://www.ucl.ac.uk/students/fees/pay-your-fees/how-to-pay")








# def add_url_to_local_files():
#     for url in UCL_URLS:
#         llm.add_url_to_local_files(WORKSPACE_NAME, url)
    
# def chat_with_llm():
#     response = llm.chat_with_workspace(WORKSPACE_NAME, "WHen is the Lunch Hour Lecture | The Global Fight Against LGBTI Rights ?")
#     print(response)
    

# def extract_data_from_text_response(text_response):
#     prompt = "Rewrite the following text, higlighting the quantitative data: \n\n" + text_response
#     llm2 = OllamaAI(OLLAMA_API_URL, "gemma:2b")
#     response = llm2.predict(prompt)
#     print(response)
#     response = json.loads(response)
#     return response



# with open('example.json') as f:
#     data = json.load(f)

#     text_response = data['textResponse']
#     sources = data['sources']
    
#     extract_data_from_text_response(text_response)
    
