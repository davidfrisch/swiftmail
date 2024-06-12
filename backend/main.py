from AnythingLLM_client import AnythingLLM
from constants import ANYTHING_LLM_BASE_URL, ANYTHING_LLM_TOKEN
from urls import UCL_URLS



llm = AnythingLLM(base_url=ANYTHING_LLM_BASE_URL, token=ANYTHING_LLM_TOKEN)


for url in UCL_URLS:
  llm.add_url_to_local_files("test2", url)
  
  
