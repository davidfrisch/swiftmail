import sys, os
from constants import ANYTHING_LLM_TOKEN, ANYTHING_LLM_BASE_URL
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from LLM.AnythingLLM_client import AnythingLLMClient
from LLM.OllamaLLM import OllamaAI
from dataset.urls import UCL_URLS

anythingllm_client = AnythingLLMClient(ANYTHING_LLM_BASE_URL, ANYTHING_LLM_TOKEN)
WORKSPACE_NAME="second_workspace"

workspaces = anythingllm_client.get_all_workspaces()['workspaces']
workspaces_names = [workspace['name'] for workspace in workspaces]



def add_url_to_workspace(workspace_name, url):
    if workspace_name not in workspaces_names:
        raise f"Workspace {workspace_name} does not exist"
      
    workspace_slug = get_workspace_slug(workspace_name)
    anythingllm_client.add_url_to_workspace(workspace_slug, url)



def get_workspace_slug(workspace_name):
    for workspace in workspaces:
        if workspace['name'] == workspace_name:
            return workspace['slug']
    return None


def main(url: str):
  print(f"URL: {url}")
  print("-------------------")
  add_url_to_workspace(WORKSPACE_NAME, url)
  
if __name__ == "__main__":
    for url in UCL_URLS:
        try:
          main(url)
        except Exception as e:
          print(f"Error: {e}")