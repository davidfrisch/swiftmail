import requests
from .anything_llm_utils import extract_urls
from logging import getLogger
logger = getLogger(__name__)
logger.setLevel("INFO")

class AnythingLLMClient:
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


  def get_document(self, document_name: str):
    documents = self.see_local_files()
    folders = documents["items"]
    for folder in folders:
      if folder["name"] == document_name:
        return folder
    return None


  def get_url_from_folder(self, folder: dict, url: str):
    for item in folder["items"]:
      if item["chunkSource"] == "link://"+url:
        return item
    return None

  def check_auth_jwt(self):
    response = self._make_request("GET", "v1/auth")
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
    response = self._make_request("POST", "v1/document/create-folder", payload)
    
    if response["success"] != True:
      logger.error(f"[FAILED] {response['message']}")
    
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
  
  def get_workspace_slug(self, category):
    workspaces = self.get_all_workspaces()['workspaces']
    for workspace in workspaces:
        if workspace['name'] == category:
            return workspace['slug']
    return None

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
  
  def __upload_link_to_workspace(self, slug, link) -> None:
    payload = {
      "link": link
    }
    response = self._make_request("POST", f"workspace/{slug}/upload-link", payload)
    if response["success"] != True:
      raise ValueError(response)
    
    return


  def embed_document_into_workspace(self, slug, adds: list = [], deletes: list = []):
    """Adds and deletes are lists of document IDs."""
    payload = {
      "adds": adds,
      "deletes": deletes
    }

    response = self._make_request("POST", f"v1/workspace/{slug}/update-embeddings", payload)
    return response
  
  def add_url_to_workspace(self, slug, url):
    localFiles = self.see_local_files()
    already_urls = extract_urls(localFiles)
    
    if url in already_urls:
        logger.error(f"[WARNING] URL {url} already exists in local files")
    else:
        logger.info(f"[SUCCESS] Adding URL {url} to local files")
        self.__upload_link_to_workspace(slug, url)
    document = self.get_document("custom-documents")
    url_elem = self.get_url_from_folder(document, url)
    elem_to_add = "custom-documents/"+url_elem["name"]
    self.embed_document_into_workspace(slug, adds=[elem_to_add])


  def delete_workspace(self, slug):
    response = self._make_request("DELETE", f"workspace/{slug}")
    return response

  def chat_with_workspace(self, slug, message, mode: str = "chat"):
    if mode not in ["chat", "query"]:
      raise ValueError("mode must be either 'chat' or 'query'")
    
    payload = {
      "message": message,
      "mode": mode
    }
    response = self._make_request("POST", f"v1/workspace/{slug}/chat", payload)
    return response
  