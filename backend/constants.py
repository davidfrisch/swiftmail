from dotenv import load_dotenv
load_dotenv()
import os 

ENV_ANYTHING_LLM_TOKEN = os.getenv("ANYTHING_LLM_TOKEN")

if not ENV_ANYTHING_LLM_TOKEN:
    raise ValueError("ANYTHING_LLM_TOKEN is not set in .env file")


ANYTHING_LLM_TOKEN = ENV_ANYTHING_LLM_TOKEN
ANYTHING_LLM_BASE_URL = "http://localhost:3001/api"
