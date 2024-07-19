from dotenv import load_dotenv
load_dotenv()
import os 

ENV_ANYTHING_LLM_TOKEN = os.getenv("ANYTHING_LLM_TOKEN")
ENV_OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")

if not ENV_ANYTHING_LLM_TOKEN:
    raise ValueError("ANYTHING_LLM_TOKEN is not set in .env file")

if not ENV_OLLAMA_API_URL:
    raise ValueError("OLLAMA_API_URL is not set in .env file")

ANYTHING_LLM_TOKEN = ENV_ANYTHING_LLM_TOKEN
ANYTHING_LLM_BASE_URL = "http://localhost:3001/api"

OLLAMA_API_URL = ENV_OLLAMA_API_URL


NO_ANSWERS_TEMPLATE = {
  "general": "Sorry, I don't have an answer for this question. Category: general",
  "Applications": "Sorry, I don't have an answer for this question. Category: Applications",
  "Entry requirements": "Sorry, I don't have an answer for this question. Category: Entry requirements",
  "Application fees": "Sorry, I don't have an answer for this question. Category: Application fees",
  "References for application": "Sorry, I don't have an answer for this question. Category: References for application",
  "Updating your application": "Sorry, I don't have an answer for this question. Category: Updating your application",
  "Application status": "Sorry, I don't have an answer for this question. Category: Application status",
  "Offers of admission": "Sorry, I don't have an answer for this question. Category: Offers of admission",
  "Tuition fees": "Sorry, I don't have an answer for this question. Category: Tuition fees",
  "Student visas": "Sorry, I don't have an answer for this question. Category: Student visas",
  "Others": "Sorry, I don't have an answer for this question. Category: Others"
}


WORKSPACE_CATEGORIES = [
  "Applications",
  "Entry requirements",
  "Application fees",
  "References for application",
  "Updating your application",
  "Application status",
  "Offers of admission",
  "Tuition fees",
  "Student visas",
  "Accommodation",
  "General"
]