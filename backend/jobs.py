from .database.models import JobStatus
from .database import crud, schemas
from .database.schemas import Email, Job
from sqlalchemy.orm import Session
from .Generater import Generater
from datetime import datetime


def extract_questions_from_email(db: Session, email: Email, generater: Generater):
    extract_questions = generater.extract_questions_from_text(email.body)
    
    for question in extract_questions:
        print(question)
        new_extract_result = schemas.ExtractResultCreate(
            email_id=email.id,
            category=question['category'] if 'category' in question else None,
            question_text=question['question'],
            extracted_at=datetime.now(),
            is_answered=False
        )
        crud.create_extract_result(db, new_extract_result)
    
    return extract_questions


def answer_questions(db: Session, generater: Generater, email: Email):
    extract_results = crud.get_extract_results_by_email_id(db, email.id)
    answers = generater.answer_questions(extract_results)
    for answer in answers:
        find_extract_result = next((x for x in extract_results if x.question_text == answer['question']), None)
        if find_extract_result:
            new_answer_result = schemas.AnswerResultCreate(
                extract_result_id=find_extract_result.id,
                answer_text=answer['answer'],
                answered_at=datetime.now()
            )
            crud.create_answer_result(db, new_answer_result)
        else:
            print(f"Could not find question: {answer['question']}")
            
    return answers


def start_job_generater(db: Session, generater: Generater, email: Email, job: Job):
    # crud.update_job_status(db, job, JobStatus.EXTRACTING)
    # extract_questions_from_email(db, email, generater)
    
    crud.update_job_status(db, job, JobStatus.ANSWERING)
    answer_questions(db, generater, email)
    
    # crud.update_job_status(db, job, JobStatus.DRAFTING)
    # generater.generate_response_email(email, generater.answers)
    
    # crud.update_job_status(db, job, JobStatus.COMPLETED)
    # job.generated_draft_email = generater.generated_draft_email