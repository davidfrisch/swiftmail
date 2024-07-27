import sys 
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from tasks.Generater import Generater
from LLM.OllamaLLM import OllamaAI
from pysimilar import compare
from time import time


def run_benchmark(generater: Generater, data: dict):
    results = {}
    start_time = time()

    original_questions = data['questions']
    extracted_questions = generater.extract_questions_from_text(data['email'])
    
    
    if len(original_questions) == len(extracted_questions):
        for i in range(len(original_questions)):
            original_question = original_questions[i]['question']
            original_category = original_questions[i]['category']
            
            extracted_question = extracted_questions[i]['question']
            extracted_category = extracted_questions[i]['category']
            
            similarity_score = compare(original_question, extracted_question)
            
            print(f"Original Question: {original_question}")
            print(f"Extracted Question: {extracted_question}")
            print(f"Similarity Score: {similarity_score}")
            print("\n")
            
            result = {
                "original_question": original_question,
                "extracted_question": extracted_question,
                "original_category": original_category,
                "extracted_category": extracted_category,
                "similarity_score": similarity_score
            }
            
            results[f"question_{i}"] = result
            results["original_questions"] = original_questions
            results["extracted_questions"] = extracted_questions
            results["success"] = True
            
    else:
        print("Number of questions extracted does not match number of original questions")
        results["original_questions"] = original_questions
        results["extracted_questions"] = extracted_questions
        results["error"] = "Number of questions extracted does not match number of original questions"
        results["success"] = False
        
    results["total_time"] = time() - start_time
    return results
            

    



def main():
    llm = OllamaAI('http://localhost:11434', 'llama3:instruct')
    generater = Generater(ollama_client=llm)
    path_folder = '../../tasks/dataset'
    benchmark_results = {}
    benchmark_file_path = './results/benchmark_results.json'
    start_time = time()
    
    for filename in os.listdir(path_folder):
        filename_path = os.path.join(path_folder, filename)
        if filename_path.endswith('.json') and "fake" in filename:
            print(f"Running benchmark for {filename}")
            with open(filename_path, 'r') as f:
                data = json.load(f)
            
            results = run_benchmark(generater, data)
            benchmark_results[filename] = results
          


    benchmark_results["total_time"] = time() - start_time
    with open(benchmark_file_path, 'w') as f:
        json.dump(benchmark_results, f)
    
    
    
    

if __name__ == "__main__":
    print("Running benchmarking script")
    main()