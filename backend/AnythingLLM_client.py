import requests
from anything_llm_utils import extract_urls
from logging import getLogger
logger = getLogger(__name__)

class AnythingLLM:
  def __init__(self, base_url, token):
    self.base_url = base_url
    self.token = token

  def _make_request(self, method, endpoint, payload=None, files=None):
    headers = {
      "Authorization": f"Bearer {self.token}"
    }
    url = f"{self.base_url}/{endpoint}"
    response = requests.request(method, url, headers=headers, json=payload, files=files)
    return response.json()

  def ping_alive(self):
    response = self._make_request("GET", "ping")
    return response

  def run_migrations(self):
    response = self._make_request("GET", "migrate")
    return response

  def check_setup(self):
    response = self._make_request("GET", "setup-complete")
    return response

  def get_vector_count(self):
    response = self._make_request("GET", "system/system-vectors")
    return response

  def see_local_files(self):
    """Get a list of all files in the local files."""
    response = self._make_request("GET", "system/local-files")
    return response["localFiles"]

  def check_auth_jwt(self):
    response = self._make_request("GET", "system/check-token")
    return response

  def request_auth_jwt(self, password):
    payload = {
      "password": password
    }
    response = self._make_request("POST", "request-token", payload)
    return response

  def check_document_processor_status(self):
    response = self._make_request("GET", "system/document-processing-status")
    return response

  def get_valid_document_types(self):
    response = self._make_request("GET", "system/accepted-document-types")
    return response
  
  def create_local_folder(self, folder_name):
    payload = {
      "name": folder_name
    }
    response = self._make_request("POST", "api/document/create-folder", payload)
    return response


  def new_workspace(self, name):
    payload = {
      "name": name
    }
    response = self._make_request("POST", "workspace/new", payload)
    return response

  def get_all_workspaces(self):
    response = self._make_request("GET", "workspaces")
    return response

  def get_workspace(self, slug):
    response = self._make_request("GET", f"workspace/{slug}")
    return response

  def get_workspace_chats(self, slug):
    response = self._make_request("GET", f"workspace/{slug}/chats")
    return response

  def update_workspace(self, slug, name, openAiTemp):
    payload = {
      "name": name,
      "openAiTemp": openAiTemp
    }
    response = self._make_request("POST", f"workspace/{slug}/update", payload)
    return response

  def upload_document_to_workspace(self, slug, file_path):
    files = {
      "file": open(file_path, 'rb')
    }
    response = self._make_request("POST", f"workspace/{slug}/upload", files=files)
    return response
  
  def upload_link_to_workspace(self, slug, link):
    payload = {
      "link": link
    }
    response = self._make_request("POST", f"workspace/{slug}/upload-link", payload)
    return response

  def embed_document_into_workspace(self, slug, adds, deletes):
    """Adds and deletes are lists of document IDs."""
    payload = {
      "adds": adds,
      "deletes": deletes
    }
    response = self._make_request("POST", f"workspace/{slug}/update-embeddings", payload)
    print(response)
    return response
  
  def add_url_to_local_files(self, slug, url):
    localFiles = self.see_local_files()
    already_urls = extract_urls(localFiles)
    
    if url in already_urls:
        logger.error(f"[FAILED] URL {url} already exists in local files")
        return 
      
    self.upload_link_to_workspace(slug, url)


  def delete_workspace(self, slug):
    response = self._make_request("DELETE", f"workspace/{slug}")
    return response

  def chat_with_workspace(self, slug, message, mode):
    if mode not in ["chat", "query"]:
      raise ValueError("mode must be either 'chat' or 'query'")
    
    payload = {
      "message": message,
      "mode": mode
    }
    response = self._make_request("POST", f"v1/workspace/{slug}/chat", payload)
    return response
  