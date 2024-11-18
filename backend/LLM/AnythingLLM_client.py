import requests
from .anything_llm_utils import extract_urls
from logging import getLogger
import shutil 
logger = getLogger(__name__)
logger.setLevel("INFO")
import os
class AnythingLLMClient:
  def __init__(self, base_url, token):
    self.base_url = base_url
    self.token = token

  def _make_request(self, method, endpoint, payload=None, files=None):

    headers = {
      "Authorization": f"Bearer {self.token}"
    }
    url = f"{self.base_url}/{endpoint}"
    try:
        response = requests.request(method, url, headers=headers, json=payload, files=files)
        if response.status_code != 200:
            logger.error(f"{response.json()}")
        return response.json()
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        raise e

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


  def get_folder(self, document_name: str):
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
    response = self._make_request("GET", "v1/workspaces")
    return response

  def get_workspace(self, slug):
    response = self._make_request("GET", f"workspace/{slug}")
    return response
  
  def get_workspace_slug(self, name):
    workspaces = self.get_all_workspaces()['workspaces']
    for workspace in workspaces:
        if workspace['name'] == name:
            return workspace['slug']
    return None

  def get_workspace_chats(self, slug):
    response = self._make_request("GET", f"v1/workspace/{slug}/chats")
    return response

  def update_workspace(self, slug, payload):
    """
    "chatProvider"
    "chatMode"
    "openAiHistory"
    "openAiPrompt"
    "queryRefusalResponse"
    "openAiTemp"
    """
    response = self._make_request("POST", f"workspace/{slug}/update", payload)
    return response

  def get_threads(self, slug):
    response = self._make_request("GET", f"workspace/{slug}/threads")
    threads = response["threads"]
    return threads
  
  def update_thread(self, slug_workspace, slug_thread, payload):
    self._make_request("POST", f"v1/workspace/{slug_workspace}/thread/{slug_thread}/update", payload)
    
  
  def new_thread(self, slug_workspace, name):
    print(f"Creating new thread with name: {name} in workspace: {slug_workspace}")
    self._make_request("POST", f"v1/workspace/{slug_workspace}/thread/new")
    threads = self.get_threads(slug_workspace)
    thread_with_same_name = [thread for thread in threads if thread["name"].split("-copy-")[0] == name]
    if len(thread_with_same_name) == 1:
        name = name + "-copy-1"
    elif len(thread_with_same_name) > 1:
        biggest_number = max([int(thread["name"].split("-copy-")[1]) if "-copy-" in thread["name"] else 0 for thread in thread_with_same_name])
        name = name + "-copy-" + str(biggest_number+1)
    
    latest_thread = sorted(threads, key=lambda x: x["createdAt"], reverse=True)[0]
    self.update_thread(slug_workspace, latest_thread["slug"], {"name": name})
    return latest_thread
  
  def delete_thread(self, slug_workspace, slug_thread):
    try:
        self._make_request("DELETE", f"workspace/{slug_workspace}/thread/{slug_thread}")
    except Exception as e:
        logger.error(f"[ERROR] {e}")
        return False
    
  def chat_with_thread(self, slug_workspace, slug_thread, message, mode: str = "chat"):
    if mode not in ["chat", "query"]:
      raise ValueError("mode must be either 'chat' or 'query'")
    
    payload = {
      "message": message,
      "mode": mode
    }
    response = self._make_request("POST", f"v1/workspace/{slug_workspace}/thread/{slug_thread}/chat", payload)
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
    document = self.get_folder("custom-documents")
    url_elem = self.get_url_from_folder(document, url)
    elem_to_add = "custom-documents/"+url_elem["name"]
    self.embed_document_into_workspace(slug, adds=[elem_to_add])


  def delete_workspace(self, slug):
    response = self._make_request("DELETE", f"workspace/{slug}")
    return response

  def chat_with_workspace(self, slug_workspace, message, mode: str = "chat"):
    if mode not in ["chat", "query"]:
      raise ValueError("mode must be either 'chat' or 'query'")
    
    payload = {
      "message": message,
      "mode": mode
    }
    response = self._make_request("POST", f"v1/workspace/{slug_workspace}/chat", payload)
    return response
  
  def save_draft_in_db(self, workspace_name, email_id, draft):
    workspace_slug = self.get_workspace_slug(workspace_name)
    folder_name = "./saved_results"
    os.makedirs(folder_name, exist_ok=True)
    filename = f"email-{email_id}.txt"
    fullpath = f"{folder_name}/{filename}"
    with open(fullpath, "w") as f:
      f.write(draft)
    
    filepath = os.path.abspath(fullpath)
    self.upload_document_to_workspace(workspace_slug, filepath)
    
    folder = self.get_folder("custom-documents")
    document_name = next(item["name"] for item in folder["items"] if item["title"] == filename)
    if not document_name:
      raise ValueError(f"Document {fullpath} not found in custom-documents folder")
    elem_to_add = "custom-documents/"+document_name
    self.embed_document_into_workspace(workspace_slug, adds=[elem_to_add])
  