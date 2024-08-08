
import sys 
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))
from Reviewer import Reviewer
from LLM.OllamaLLM import OllamaAI
from datetime import datetime
from datetime import datetime
from database import schemas

# Load the questions
answer_questions_path = "/Users/david/development/ucl/res_project/swiftmail/benchmarking/answer_questions/results/benchmar_results_responses_2.json"
draft_generated_path = "../draft_emails/results/benchmark_0808.json"

with open(answer_questions_path, 'r') as f:
    answer_questions_data = json.load(f)
    
with open(draft_generated_path, 'r') as f:
    draft_generated_data = json.load(f)

generated_answers: schemas.AnswerResult = []
generated_draft = []
question_id = 0
email_id = 0
answer_id = 0
results = []


model_name = 'llama3.1:latest'
llm = OllamaAI('http://localhost:11434', model_name)
reviewer = Reviewer(llm)


scores_path = f'./results/benchmark_results_draft_reviewer_{datetime.now()}.json'


for email in answer_questions_data["results"]:
    print(email)
    
    generated_answers_raw = answer_questions_data["results"][email]
    generated_answers = []
    for generated_answer_raw in generated_answers_raw:
        generated_answers.append(schemas.AnswerResult(
            id=answer_id,
            question_id=question_id,
            answer_text=generated_answer_raw["generated_answer"],
            answered_at=datetime.now(),
            email_id=email_id,
            sources=json.dumps(generated_answer_raw["sources"]),
            job_id=email_id,
            extract_result_id=question_id
        ))
    
        question_id += 1
        email_id += 1
        answer_id += 1
        
    generated_draft_text = draft_generated_data["results"][email]["generated_text"]
    
    scores = reviewer.evaluate_draft_email(generated_draft_text, generated_answers)

    
    
    

    


if not os.path.exists('./results'):
    os.makedirs('./results')

with open(scores_path, 'w') as f:
    json.dump(scores, f, indent=4)
    print(f"Results saved to {scores_path}")