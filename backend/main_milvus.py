from pymilvus import connections
from pymilvus import CollectionSchema, FieldSchema, DataType, Collection
from langchain_community.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

client = connections.connect(
  alias="default", 
  host='localhost', 
  port='19530'
)


loader = WebBaseLoader("https://www.ucl.ac.uk/students/fees/pay-your-fees/when-to-pay")
docs = loader.load()

embeddings = OllamaEmbeddings(model="all-minilm:l6-v2")
text_splitter = RecursiveCharacterTextSplitter()
split_documents = text_splitter.split_documents(docs)

print(split_documents[0].metadata)