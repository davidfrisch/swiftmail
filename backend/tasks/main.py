import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from LLM.OllamaLLM import OllamaAI
from AnythingLLM_client import AnythingLLMClient
from extract_questions import extract_questions_from_text
from answer_questions import answer_question
from generate_response_email import generate_response_email

def main():
    llm = OllamaAI('http://localhost:11434', 'llama3:latest')
    anything_llm_client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")

    with open('original_email_1.txt', 'r') as f:
        text = f.read()
    
    questions = extract_questions_from_text(llm, text)
    print(questions)
    for question in questions:
        answer = answer_question(anything_llm_client, question)
        question['answer'] = answer

    response_email = generate_response_email(llm, text, questions)
    print(response_email)
    
if __name__ == '__main__':
    main()