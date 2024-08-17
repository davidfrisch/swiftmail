import sys 
import os
import json
from time import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from dataset.bank_questions import ucl_questions
from backend.Generater import Generater
from backend.LLM.OllamaLLM import OllamaAI
from backend.LLM.AnythingLLM_client import AnythingLLMClient
from backend.database import schemas


def run_benchmark(generater: Generater, data: dict):
    generated_questions = data['questions']
    questions = []
    answers = []
    email = schemas.Email(
        subject=data['email'].split('\n\n')[0].replace('Subject: ', ''),
        body="\n\n".join(data['email'].split('\n\n')[1:]),
        id=-1,
    )
    for i, generated_question in enumerate(generated_questions):
        question_text = generated_question['question']
        answer_text = generated_question['answer']

        answer = schemas.AnswerResult(
            answer_text=answer_text,
            id=i,
            job_id=-1,
            extract_result_id=i,
            
        )
        question = schemas.ExtractResult(
            question_text=question_text,
            id=i,
            job_id=-1,
            problem_context="",
        )
        question.answer = answer
        
        questions.append(question)
        answers.append(answer)
        
    start_time = time()
    generated_text = generater.generate_response_email(email, questions, answers)
    
    
    return {
        "generated_text": generated_text,
        "time": time() - start_time,
    }
        
  
            
def main():
    llm = OllamaAI('http://localhost:11434', 'llama3:instruct')
    anything_llm_client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")
    generater = Generater(ollama_client=llm, anyllm_client=anything_llm_client)
    path_folder = '../../dataset'
    benchmark_results = { "results": {} }
    benchmark_file_path = f'./results/benchmark_results_responses_{time()}.json'
    os.makedirs(os.path.dirname(benchmark_file_path.replace('benchmark_results_responses.json', '')), exist_ok=True)
    start_time = time()
    
    for filename in os.listdir(path_folder):
        filename_path = os.path.join(path_folder, filename)
        if filename_path.endswith('.json') and "fake" in filename:
            print(f"Running benchmark for {filename}")
            with open(filename_path, 'r') as f:
                data = json.load(f)                
            
            results = run_benchmark(generater, data)
            benchmark_results["results"][filename] = results
          


    benchmark_results["total_time"] = time() - start_time
    with open(benchmark_file_path, 'w') as f:
        json.dump(benchmark_results, f)
    
    
    
    

if __name__ == "__main__":
    print("Running benchmarking script")
    main()