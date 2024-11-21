from .database.models import JobStatus
from .database import crud, schemas, create_database, models, schemas
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from contextlib import contextmanager
from .Generater import Generater
from datetime import datetime
import endpoints_models
import logging
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_questions_from_email(db: Session, generater: Generater, email: schemas.Email, job: schemas.Job):
    extract_questions = generater.extract_questions_from_text(email.body)
    
    for question in extract_questions:
        new_extract_result = schemas.ExtractResultCreate(
            email_id=email.id,
            job_id=job.id,
            problem_context=question['problem_context'],
            question_text=question['extract_text'],
            extracted_at=datetime.now(),
            is_answered=False
        )
        crud.create_extract_result(db, new_extract_result)
    
    return extract_questions


def answer_questions(db: Session, generater: Generater, email: schemas.Email, job: schemas.Job, thread_slug):
    extract_results = crud.get_extract_results_by_job_id(db, job.id)
    answers = generater.answer_questions(email, extract_results, thread_slug)
    for answer in answers:
        find_extract_result = next((x for x in extract_results if x.question_text == answer['question']), None)
        if find_extract_result:
            new_answer_result = schemas.AnswerResultCreate(
                extract_result_id=find_extract_result.id,
                job_id=job.id,
                sources=json.dumps(answer['sources']),
                unique_sources=json.dumps(answer['unique_sources']),
                answer_text=answer['answer'],
                answered_at=datetime.now()
            )
            crud.create_answer_result(db, new_answer_result)
        else:
            print(f"Could not find question: {answer['question']}")
            
    return answers


def update_answer(db: Session, generater: Generater, answer: schemas.AnswerResult, req_body: endpoints_models.Feedback):
    
    job = crud.get_job(db, answer.job_id)
    
    extract_result = crud.get_extract_result(db, answer.extract_result_id)
    feedback = f"Previous answer was: \n -start- {answer.answer_text} -end-.\n The user feedback was: {req_body.feedback}.\n Retry the answer considering the user feedback."
    
    new_answer_text, unique_sources, _ = generater.answer_question(extract_result.problem_context, extract_result.question_text, feedback, job.slug_thread)
    answer.answer_text = new_answer_text
    answer.sources = json.dumps(unique_sources)
    answer.answered_at = datetime.now()
    answer.binary_score = None
    answer.linkert_score = None
    answer.hallucination_score = None
    
    new_answer = crud.update_answer_result(db, answer)
    
    return new_answer
    

def generate_draft_email(db: Session, generater: Generater, email: schemas.Email, job: schemas.Job, thread_slug):
    # extract_results = crud.get_extract_results_by_job_id(db, job.id)
    # answers = crud.get_answer_results_by_job_id(db, job.id)
    
    draft_response = generater.generate_response_email(email, [], [], email.additional_information, thread_slug)

    draft_body = draft_response['textResponse']
    sources = draft_response['sources']
    
    new_draft_result = schemas.DraftResultCreate(
        job_id=job.id,
        email_id=email.id,
        draft_body=draft_body,
        sources = json.dumps(sources),
        created_at=datetime.now(),
    )
    
    crud.create_draft_result(db, new_draft_result)
    return draft_response
    

def retry_draft_email(db: Session, generater: Generater, draft: schemas.DraftResult, feedback: endpoints_models.Feedback):
    original_draft = draft.draft_body
    draft_response = generater.regenerate_response_email(original_draft, feedback.feedback) 
    draft.draft_body = draft_response
    new_draft = crud.update_draft_result(db, draft)
    
    return new_draft


@contextmanager
def get_db_session():
    engine = create_engine(create_database.SQLITE3_DATABASE_URL)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def start_job_generater(ollama_client, anyllm_client, email_id, job_id, thread_slug):
    try:
        logger.info("Starting job generator for email_id: %s, job_id: %s", email_id, job_id)
        generater = Generater(ollama_client, anyllm_client)
        with get_db_session() as db:
            email = crud.get_email(db, email_id)
            job = crud.get_job(db, job_id)
            
            crud.update_job_status(db, job, JobStatus.EXTRACTING)
            crud.update_job(db, job)
            
            # logger.info("Job status updated to EXTRACTING")
            # extract_questions_from_email(db, generater, email, job)
            
            # crud.update_job_status(db, job, JobStatus.ANSWERING)
            # logger.info("Job status updated to ANSWERING")
            # answer_questions(db, generater, email, job, thread_slug)
            
            crud.update_job_status(db, job, JobStatus.DRAFTING)
            
            
            logger.info("Job status updated to DRAFTING")
            generate_draft_email(db, generater, email, job, thread_slug)
            
            crud.update_job_status(db, job, JobStatus.COMPLETED)
            logger.info("Job status updated to COMPLETED")
    
    except Exception as e:
        logger.error("An error occurred: %s", e, exc_info=True)
        with get_db_session() as db:
            job = crud.get_job(db, job_id)
            crud.update_job_status(db, job, JobStatus.FAILED)
            logger.info("Job status updated to FAILED")
        
    
    
    

