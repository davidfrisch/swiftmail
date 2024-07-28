from .database.models import JobStatus
from .database import crud, schemas
from .database.schemas import Email, Job
from sqlalchemy.orm import Session
from .Generater import Generater
from datetime import datetime
import endpoints_models


def extract_questions_from_email(db: Session, generater: Generater, email: Email, job: Job):
    extract_questions = generater.extract_questions_from_text(email.body)
    
    for question in extract_questions:
        new_extract_result = schemas.ExtractResultCreate(
            email_id=email.id,
            job_id=job.id,
            category=question['category'] if 'category' in question else None,
            question_text=question['question'],
            extracted_at=datetime.now(),
            is_answered=False
        )
        crud.create_extract_result(db, new_extract_result)
    
    return extract_questions


def answer_questions(db: Session, generater: Generater, job: Job):
    extract_results = crud.get_extract_results_by_job_id(db, job.id)
    answers = generater.answer_questions(extract_results)
    for answer in answers:
        find_extract_result = next((x for x in extract_results if x.question_text == answer['question']), None)
        if find_extract_result:
            new_answer_result = schemas.AnswerResultCreate(
                extract_result_id=find_extract_result.id,
                job_id=job.id,
                answer_text=answer['answer'],
                answered_at=datetime.now()
            )
            crud.create_answer_result(db, new_answer_result)
        else:
            print(f"Could not find question: {answer['question']}")
            
    return answers


def update_answer(db: Session, generater: Generater, answer: schemas.AnswerResult, req_body: endpoints_models.Feedback):
    extract_result = crud.get_extract_result(db, answer.extract_result_id)
    feedback = f"Previous answer was: \n -start- {answer.answer_text} -end-.\n The user feedback was: {req_body.feedback}.\n Retry the answer considering this feedback."
    
    new_answer_text, _, _ = generater.answer_question(extract_result.question_text, feedback)
    answer.answer_text = new_answer_text
    new_answer = crud.update_answer_result(db, answer)
    
    return new_answer
    

def generate_draft_email(db: Session, generater: Generater, email: Email, job: Job):
    extract_results = crud.get_extract_results_by_job_id(db, job.id)
    answers = crud.get_answer_results_by_job_id(db, job.id)
    draft_response = generater.generate_response_email(email, extract_results, answers)
    
    new_draft_result = schemas.DraftResultCreate(
        job_id=job.id,
        email_id=email.id,
        draft_body=draft_response,
        created_at=datetime.now(),
    )
    
    crud.create_draft_result(db, new_draft_result)
    return draft_response
    

def update_draft_email(db: Session, generater: Generater, draft: schemas.DraftResult, feedback: endpoints_models.Feedback):
    email = crud.get_email(db, draft.email_id)
    questions = crud.get_extract_results_by_job_id(db, draft.job_id)
    answers = crud.get_answer_results_by_job_id(db, draft.job_id)
    
    draft_response = generater.generate_response_email(email, questions, answers, feedback.feedback) 
    draft.draft_body = draft_response
    new_draft = crud.update_draft_result(db, draft)
    
    return new_draft


def start_job_generater(db: Session, generater: Generater, email: Email, job: Job):
    crud.update_job_status(db, job, JobStatus.EXTRACTING)
    extract_questions_from_email(db, generater, email, job)
    
    crud.update_job_status(db, job, JobStatus.ANSWERING)
    answer_questions(db, generater, job)
    
    crud.update_job_status(db, job, JobStatus.DRAFTING)
    generate_draft_email(db, generater, email, job)
    
    crud.update_job_status(db, job, JobStatus.COMPLETED)
    
    extract_results = crud.get_extract_results_by_job_id(db, job.id)
    answers = crud.get_answer_results_by_job_id(db, job.id)
    draft_result = crud.get_draft_results_by_job_id(db, job.id)
    
    return {
        "extract_results": extract_results,
        "answers": answers,
        "draft_result": draft_result
    }
