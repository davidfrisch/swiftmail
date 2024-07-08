import os 
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from LLM.OllamaLLM import OllamaAI
from extract_questions import extract_questions_from_text

def main():
    llm = OllamaAI('http://localhost:11434', 'llama3:latest')
    with open('original_email_1.txt', 'r') as f:
        text = f.read()
    
    questions = extract_questions_from_text(llm, text)
    print(questions)
    
if __name__ == '__main__':
    main()