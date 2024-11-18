from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from time import time
## Emails
def get_emails(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Email]:
    return db.query(models.Email).offset(skip).limit(limit).all()
  
def get_email(db: Session, email_id: int) -> schemas.Email:
    return db.query(models.Email).filter(models.Email.id == email_id).first()

def create_email(db: Session, email: schemas.Email):
    db_email = models.Email(subject=email.subject, body=email.body, workspace_name=email.workspace_name)
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email

def update_email(db: Session, email: models.Email):
    db.commit()
    db.refresh(email)
    return email

## ExtractResult
def get_extract_results(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.ExtractResult]:
    return db.query(models.ExtractResult).offset(skip).limit(limit).all()
  
def get_extract_result(db: Session, extract_result_id: int) -> schemas.ExtractResult:
    return db.query(models.ExtractResult).filter(models.ExtractResult.id == extract_result_id).first()

def get_extract_results_by_job_id(db: Session, job_id: int) -> List[schemas.ExtractResult]:
    return db.query(models.ExtractResult).filter(models.ExtractResult.job_id == job_id).all()

def get_extract_results_by_email_id(db: Session, email_id: int) -> List[schemas.ExtractResult]:
    return db.query(models.ExtractResult).filter(models.ExtractResult.email_id == email_id).all()
  
def create_extract_result(db: Session, extract_result: schemas.ExtractResult):
    db_extract_result = models.ExtractResult(**extract_result.model_dump())
    db.add(db_extract_result)
    db.commit()
    db.refresh(db_extract_result)
    return db_extract_result
  

## AnswerResult
def get_answer_results(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AnswerResult).offset(skip).limit(limit).all()
  
def get_answer_result(db: Session, answer_result_id: int) -> schemas.AnswerResult:
    return db.query(models.AnswerResult).filter(models.AnswerResult.id == answer_result_id).first()
  
def get_answer_results_by_extract_result_id(db: Session, extract_result_id: int) -> List[schemas.AnswerResult]:
    return db.query(models.AnswerResult).filter(models.AnswerResult.extract_result_id == extract_result_id).all()

def get_answer_results_by_email_id(db: Session, email_id: int) -> List[schemas.AnswerResult]:
    return db.query(models.AnswerResult).join(models.ExtractResult).filter(models.ExtractResult.email_id == email_id).all()

def get_answer_results_by_job_id(db: Session, job_id: int) -> List[schemas.AnswerResult]:
    return db.query(models.AnswerResult).join(models.ExtractResult).filter(models.ExtractResult.job_id == job_id).all()

def create_answer_result(db: Session, answer_result: schemas.AnswerResult):
    db_answer_result = models.AnswerResult(**answer_result.model_dump())
    db.add(db_answer_result)
    db.commit()
    db.refresh(db_answer_result)
    return db_answer_result
  
def update_answer_result(db: Session, answer_result: models.AnswerResult):
    db.commit()
    db.refresh(answer_result)
    return answer_result

## DraftResult
def get_draft_results(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DraftResult).offset(skip).limit(limit).all()
  
def get_draft_result(db: Session, draft_result_id: int) -> schemas.DraftResult:
    return db.query(models.DraftResult).filter(models.DraftResult.id == draft_result_id).first()

def get_draft_results_by_email_id(db: Session, email_id: int):
    return db.query(models.DraftResult).filter(models.DraftResult.email_id == email_id).all()

def get_draft_results_by_job_id(db: Session, job_id: int) -> List[schemas.DraftResult]:
    return db.query(models.DraftResult).filter(models.DraftResult.job_id == job_id).all()

def create_draft_result(db: Session, draft_result: schemas.DraftResult):
    db_draft_result = models.DraftResult(**draft_result.model_dump())
    db.add(db_draft_result)
    db.commit()
    db.refresh(db_draft_result)
    return db_draft_result

def update_draft_result(db: Session, draft_result: models.DraftResult):
    db.commit()
    db.refresh(draft_result)
    return draft_result

# Job

def get_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Job]:
    return db.query(models.Job).offset(skip).limit(limit).all()
  
def get_job(db: Session, job_id: int) -> schemas.Job:
    return db.query(models.Job).filter(models.Job.id == job_id).first()
  
def get_jobs_by_email_id(db: Session, email_id: int) -> List[schemas.Job]:
    return db.query(models.Job).filter(models.Job.email_id == email_id).all()
  
def create_job(db: Session, job: schemas.Job):
    db_job = models.Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
  
def update_job(db: Session, job: models.Job):
    db.commit()
    db.refresh(job)
    return job
  
def update_job_status(db: Session, job: schemas.Job, status: models.JobStatus):
    job.status = status.name
    db.commit()
    db.refresh(job)
    return job