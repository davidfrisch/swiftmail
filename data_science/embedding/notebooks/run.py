import os
import sys
import lancedb
import ollama
import numpy as np
sys.path.append('../../..')
from backend.LLM.AnythingLLM_client import AnythingLLMClient


dataset_path_txt = "../../../dataset/graduate_txt/faq_txt"
EMBEDDING_MODELS = ["all-minilm:l6-v2", "nomic-embed-text:latest"]
WORKSPACE_NAME = "demo"
db = lancedb.connect("../../../anythingllm/lancedb")



def initialize_workspace():
    anyllm_client = AnythingLLMClient("http://localhost:3001/api", "YKH2935-TD9MYVY-PDCDN6H-5Z1T0YW")
    anyllm_client.ping_alive()
    return anyllm_client

    
def set_new_parameters(anyllm_client: AnythingLLMClient, embedding_model, max_embedding_size, chunk_size, chunk_overlap):
    response = anyllm_client.set_embedding_provider(embedding_model, max_embedding_size)
    response = anyllm_client.set_chunk_size(chunk_size, chunk_overlap)
    return response
    


def add_files_to_workspace(anyllm_client: AnythingLLMClient, workspace_name, dataset_path):
    files = os.listdir(dataset_path)
    for file in files:
        if file.endswith(".txt"):
            full_path = os.path.join(dataset_path, file)
            anyllm_client.add_document_to_workspace(workspace_name, full_path)
            print(f"Adding file {file} to workspace {workspace_name}")
        

tbl = db.open_table("demo")

# print(tbl.head())

embed_query = ollama.embeddings(
  model="nomic-embed-text:latest",
  prompt='Miss application deadline',
)

# print(embed_query.embedding)

df = tbl.search(embed_query.embedding) \
    .limit(4) \
    .to_df()

print(df.head())


