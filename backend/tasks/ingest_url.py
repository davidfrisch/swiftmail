import sys, os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from AnythingLLM_client import AnythingLLMClient
from LLM.OllamaLLM import OllamaAI
from constants import WORKSPACE_CATEGORIES as CATEGORIES
from langchain_community.document_loaders import WebBaseLoader

anythingllm_client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")


workspaces = anythingllm_client.get_all_workspaces()['workspaces']
workspaces_names = [workspace['name'] for workspace in workspaces]


def create_workspace(workspace_name):
    if workspace_name in workspaces_names:
        return f"Workspace {workspace_name} already exists"
    anythingllm_client.new_workspace(workspace_name)
    return f"Workspace {workspace_name} created"
  
def create_all_workspaces():
    for category in CATEGORIES:
        print(create_workspace(category))

def add_url_to_workspace(workspace_name, url):
    if workspace_name not in workspaces_names:
        return f"Workspace {workspace_name} does not exist"
      
    workspace_slug = get_workspace_slug("General")
    print(f"Workspace slug: {workspace_slug}")
    anythingllm_client.add_url_to_workspace(workspace_slug, url)
    print(f"Document added to workspace {workspace_name}")


def categorise_document(document):
    title = document[0].metadata.get("title")
    print(f"Title: {title}")
    prompt = f"""
    The possible categories are: {', '.join(CATEGORIES)}
    *Only say in what category this document can fit. If it can go to more than one category, say it is "General"*
    Title: {title}
    --
    expected output is JSON:
    {{
      "category": "[result]"
    }}
    """
    
    ollama_client = OllamaAI('http://localhost:11434', 'llama3:instruct')
    ollama_client.healht_check()
    response = ollama_client.predict(prompt, format="json")
    category = json.loads(response)["category"]
    return category


def get_workspace_slug(workspace_name):
    for workspace in workspaces:
        if workspace['name'] == workspace_name:
            return workspace['slug']
    return None


def main(url: str):
  loader = WebBaseLoader(url)
  docs = loader.load()
  category = categorise_document(docs)
  add_url_to_workspace(category, url)
  
if __name__ == "__main__":
    url = "https://www.ucl.ac.uk/prospective-students/graduate/frequently-asked-questions"
    url2 = "https://www.ucl.ac.uk/students/fees/pay-your-fees/how-to-pay"
    url2 = "https://www.ucl.ac.uk/accommodation/"
    main(url)