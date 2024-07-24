import sys 
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from tasks.Generater import Generater
from LLM.OllamaLLM import OllamaAI
from pysimilar import compare
from time import time


def main():
    llm = OllamaAI('http://localhost:11434', 'llama3:instruct')
    filename_path = '../../tasks/dataset/fake_email_2.json'
    filename = filename_path.split('/')[-1].split('.')[0]
    benchmark_file_path = f"./results/{time()}_{filename}_benchmark.json"
    benchmark_results = { "filename": filename , "date": time() }
    
    with open(filename_path, 'r') as f:
        fake_email = json.load(f)
    
    text = fake_email['email']
    original_questions = fake_email['questions']
    start_time = time()
    generater = Generater({'ollama_client': llm})
    extracted_questions = generater.extract_questions_from_text(llm, text)
    end_time = time() - start_time
    
    if len(original_questions) == len(extracted_questions):
        for i in range(len(original_questions)):
            original_question = original_questions[i]
            extracted_question = extracted_questions[i]['question']
            similarity_score = compare(original_question, extracted_question)
            
            print(f"Original Question: {original_question}")
            print(f"Extracted Question: {extracted_question}")
            print(f"Similarity Score: {similarity_score}")
            print("\n")
            
            result = {
                "original_question": original_question,
                "extracted_question": extracted_question,
                "similarity_score": similarity_score
            }
            
            benchmark_results[f"question_{i}"] = result
            benchmark_results["success"] = True
            
    else:
        print("Number of questions extracted does not match number of original questions")
        result = {
            "original_questions": original_questions,
            "extracted_questions": extracted_questions
        }
        benchmark_results["questions"] = result
        benchmark_results["error"] = "Number of questions extracted does not match number of original questions"
        benchmark_results["success"] = False
            
    benchmark_results["total_time"] = end_time
    with open(benchmark_file_path, 'w') as f:
        json.dump(benchmark_results, f)
    
    
    
    
    

if __name__ == "__main__":
    print("Running benchmarking script")
    main()