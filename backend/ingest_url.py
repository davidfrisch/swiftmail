import sys, os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from LLM.AnythingLLM_client import AnythingLLMClient
from LLM.OllamaLLM import OllamaAI
from backend.tasks.Generater.constants import WORKSPACE_CATEGORIES as CATEGORIES
from langchain_community.document_loaders import WebBaseLoader
from dataset.urls import UCL_URLS

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
        create_workspace(category)

def add_url_to_workspace(workspace_name, url):
    if workspace_name not in workspaces_names:
        return f"Workspace {workspace_name} does not exist"
      
    workspace_slug = get_workspace_slug("General")
    anythingllm_client.add_url_to_workspace(workspace_slug, url)


def categorise_document(document):
    title = document[0].metadata.get("title")
    print(f"Title: {title}")
    if "404" in title:
        raise Exception("URL is not valid")
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
  print(f"URL: {url}")
  print(f"Category: {category}")
  print("-------------------")
  add_url_to_workspace("General", url)
  
if __name__ == "__main__":
    for url in UCL_URLS:
        try:
          main(url)
        except Exception as e:
          print(f"Error: {e}")