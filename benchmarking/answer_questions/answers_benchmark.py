import sys 
import os
import json
from time import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from dataset.bank_questions import ucl_questions_undergrad
from backend.Generater import Generater
from backend.LLM.OllamaLLM import OllamaAI
from backend.LLM.AnythingLLM_client import AnythingLLMClient


def get_gold_answer(question_text):
    for question in ucl_questions_undergrad:
        if question['question'] == question_text:
            return question['answer']
          
    print(f"Could not find gold answer for question: {question_text}")
    raise Exception("Could not find gold answer for question")


def run_benchmark(generater: Generater, data: dict):
    questions = data['questions']
    results = []
    for question in questions:
        start_time = time()
        question_text = question['question']
        gold_answer = get_gold_answer(question_text)

        answer, unique_sources, sources = generater.answer_question("", question_text, "")
        print(unique_sources)
        try: 
            answer = answer.split("?\n")[1].strip()
        except:
            print(f"Did not need to split the answer: {answer}")
        result = {
            "question": question_text,
            "gold_answer": gold_answer,
            "generated_answer": answer,
            "unique_sources": unique_sources,
            "sources": sources,
            "time": time() - start_time
        }
        
        results.append(result)
        
    
    return results
        
  
            
        
    
    



def main():
    llm = OllamaAI('http://localhost:11434', 'llama3:instruct')
    anything_llm_client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")
    generater = Generater(ollama_client=llm, anyllm_client=anything_llm_client)
    path_folder = '../../dataset'
    benchmark_results = { "results": {} }
    benchmark_file_path = f'./results/benchmark_results_responses_undergrad{time()}.json'
    os.makedirs(os.path.dirname(benchmark_file_path.replace('benchmark_results_responses_undergrad.json', '')), exist_ok=True)
    start_time = time()
    
    for filename in os.listdir(path_folder):
        filename_path = os.path.join(path_folder, filename)
        if filename_path.endswith('.json') and "fake" and "undergrad" in filename:
            print(f"Running benchmark for {filename}")
            with open(filename_path, 'r') as f:
                data = json.load(f)
                results = run_benchmark(generater, data)
                
            
            results = run_benchmark(generater, data)
            benchmark_results["results"][filename] = results
          


    benchmark_results["total_time"] = time() - start_time
    with open(benchmark_file_path, 'w') as f:
        json.dump(benchmark_results, f)
    
    
    
    

if __name__ == "__main__":
    print("Running benchmarking script")
    main()