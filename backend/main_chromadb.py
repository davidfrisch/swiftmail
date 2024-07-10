import chromadb
import ollama
import json
from typing import List, Dict, Any

client = chromadb.PersistentClient(path="../chromadb/chroma")
collection = client.get_collection(name="verifier")


prompt = """
When are the deadlines for UCL payments in autumn ?
"""
num_results = 4
response = ollama.embeddings(
  prompt=prompt,
  model="nomic-embed-text"
)

results = collection.query(
  query_embeddings=[response["embedding"]],
  n_results=num_results,
)


data: List[Dict[str, Any]] = [
  { 'id' : id, 'distance' : distance, 'text' : text, 'metadata' : metadata }
  for id, distance, text, metadata in zip(results['ids'][0], results['distances'][0], results['documents'][0], results['metadatas'][0])
]


document_medatdata = data.split("\n")[1].split(":")[1].strip()

print(document_medatdata)
print("--------------------------------")
print("--------------------------------")
print("--------------------------------")

output = ollama.generate(
  model="llama3",
  prompt=f"Using this data: {data}. Respond to this prompt: {prompt}"
)

print(output["response"])

