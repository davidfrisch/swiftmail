
import sys 
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))
from Reviewer import Reviewer
from LLM.OllamaLLM import OllamaAI
from time import time
from datetime import datetime
from database import schemas

# Load the questions
answer_questions_path = "/Users/david/development/ucl/res_project/swiftmail/benchmarking/answer_questions/results/benchmar_results_responses_2.json"


with open(answer_questions_path, 'r') as f:
    answer_questions_data = json.load(f)

extracted_questions: schemas.ExtractResult = []
generated_answers: schemas.AnswerResult = []
question_id = 0
email_id = 0
answer_id = 0
results = []
for email in answer_questions_data["results"]:
    for generated_answer_raw in answer_questions_data["results"][email]:
        data = generated_answer_raw
        question = data["question"]
        generated_answer = data["generated_answer"]
        
        question_id += 1
        email_id += 1
        answer_id += 1
        
        extracted_questions.append(schemas.ExtractResult(
          question_text=question,
          id=question_id,
          extract_text=question,
          problem_context=question,
          extracted_at=datetime.now(),
          email_id=email_id,
          job_id=email_id
        ))
        generated_answers.append(schemas.AnswerResult(
            id=answer_id,
            question_id=question_id,
            answer_text=generated_answer,
            answered_at=datetime.now(),
            email_id=email_id,
            sources=json.dumps(data["sources"]),
            job_id=email_id,
            extract_result_id=question_id
        ))
    
    

    

model_name = 'llama3.1:latest'
llm = OllamaAI('http://localhost:11434', model_name)
reviewer = Reviewer(llm)

scores =  reviewer.evaluate_answers(extracted_questions, generated_answers)

scores_path = f'./results/benchmark_results_reviewer_{time()}.json'

if not os.path.exists('./results'):
    os.makedirs('./results')

with open(scores_path, 'w') as f:
    json.dump(scores, f, indent=4)
    print(f"Results saved to ./results/benchmark_results_reviewer_{time()}.json")
