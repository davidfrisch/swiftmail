import sys 
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from tasks.Generater import Generater
from LLM.OllamaLLM import OllamaAI
from LLM.AnythingLLM_client import AnythingLLMClient
from time import time
from tasks.dataset.bank_questions import ucl_questions


def get_gold_answer(question_text):
    for question in ucl_questions:
        if question['question'] == question_text:
            return question['answer']
          
    print(f"Could not find gold answer for question: {question_text}")
    raise Exception("Could not find gold answer for question")


def run_benchmark(generater: Generater, data: dict):
    start_time = time()
    questions = data['questions']
    results = []
    for question in questions:
        question_text = question['question']
        gold_answer = get_gold_answer(question_text)
        category = question['category']
        answer, sources, total_sim_distance = generater.answer_question(question_text, category)
        results = {
            "question": question_text,
            "gold_answer": gold_answer,
            "category": category,
            "generated_answer": answer,
            "sources": sources,
            "total_sim_distance": total_sim_distance
        }
        
    results["total_time"] = time() - start_time
    return results
        
  
            
        
    
    



def main():
    llm = OllamaAI('http://localhost:11434', 'llama3:instruct')
    anything_llm_client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")
    generater = Generater(ollama_client=llm, anyllm_client=anything_llm_client)
    path_folder = '../../tasks/dataset'
    benchmark_results = {}
    benchmark_file_path = './results/benchmark_results_responses.json'
    os.makedirs(os.path.dirname(benchmark_file_path.replace('benchmark_results_responses.json', '')), exist_ok=True)
    start_time = time()
    
    for filename in os.listdir(path_folder)[:1]:
        filename_path = os.path.join(path_folder, filename)
        if filename_path.endswith('.json') and "fake" in filename:
            print(f"Running benchmark for {filename}")
            with open(filename_path, 'r') as f:
                data = json.load(f)
                results = run_benchmark(generater, data)
                
            
            results = run_benchmark(generater, data)
            benchmark_results[filename] = results
          


    benchmark_results["total_time"] = time() - start_time
    with open(benchmark_file_path, 'w') as f:
        json.dump(benchmark_results, f)
    
    
    
    

if __name__ == "__main__":
    print("Running benchmarking script")
    main()