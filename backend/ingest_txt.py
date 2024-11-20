import sys, os
from constants import ANYTHING_LLM_TOKEN, ANYTHING_LLM_BASE_URL
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from LLM.AnythingLLM_client import AnythingLLMClient
from LLM.OllamaLLM import OllamaAI


anythingllm_client = AnythingLLMClient(ANYTHING_LLM_BASE_URL, ANYTHING_LLM_TOKEN)
WORKSPACE_NAME="third_workspace"
 

def get_workspace_slug(workspace_name):
    workspaces = anythingllm_client.get_all_workspaces()['workspaces']
    workspaces_names = [workspace['name'] for workspace in workspaces]
    if WORKSPACE_NAME not in workspaces_names:
      raise f"Workspace {WORKSPACE_NAME} does not exist"
    
    for workspace in workspaces:
        if workspace['name'] == workspace_name:
            return workspace['slug']
          
    return None


def main(file_path: str):
  
  workspace_slug = get_workspace_slug(WORKSPACE_NAME)
  anythingllm_client.add_document_to_workspace(workspace_slug, file_path)

  
if __name__ == "__main__":
   # go through each file in folder and upload it to workspace
    folder_path = "../dataset/faq_txt"
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if ".txt" not in file_path:
            continue
          
        main(file_path)
        print(f"Uploaded {file_path} to workspace {WORKSPACE_NAME}")