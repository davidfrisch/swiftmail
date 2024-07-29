import sys 
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))
from Generater import Generater
from LLM.OllamaLLM import OllamaAI
from time import time
from datetime import datetime

def run_benchmark(generater: Generater, data: dict):
    results = {}
    start_time = time()

    original_questions = data['questions']
    extracted_questions = generater.extract_questions_from_text(data['email'])
    
    results["original_questions"] = original_questions
    results["extracted_questions"] = extracted_questions   
    results["extraction_time"] = time() - start_time
    
    return results
            


def main():
    model_name = 'llama3.1:latest'
    llm = OllamaAI('http://localhost:11434', model_name)
    generater = Generater(ollama_client=llm)
    path_folder = '../../dataset'
    benchmark_results = {"results": {}}
    benchmark_file_path = './results/benchmark_results.json'
    os.makedirs(os.path.dirname(benchmark_file_path.replace('benchmark_results.json', '')), exist_ok=True)
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
    benchmark_results["date"] = datetime.now().strftime("%d/%m/%Y")
    benchmark_results["model_name"] = model_name
    
    with open(benchmark_file_path, 'w') as f:
        json.dump(benchmark_results, f)
    
    
    
    

if __name__ == "__main__":
    print("Running benchmarking script")
    main()