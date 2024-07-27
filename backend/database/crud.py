from sqlalchemy.orm import Session

from . import models, schemas

## Emails
def get_emails(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Email).offset(skip).limit(limit).all()
  
def get_email(db: Session, email_id: int):
    return db.query(models.Email).filter(models.Email.id == email_id).first()

def create_email(db: Session, email: schemas.EmailCreate):
    db_email = models.Email(subject=email.subject, body=email.body, sent_at=email.sent_at, is_read=email.is_read)
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email
  

## ExtractResult
def get_extract_results(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ExtractResult).offset(skip).limit(limit).all()
  
def get_extract_result(db: Session, extract_result_id: int):
    return db.query(models.ExtractResult).filter(models.ExtractResult.id == extract_result_id).first()

def get_extract_results_by_email_id(db: Session, email_id: int):
    return db.query(models.ExtractResult).filter(models.ExtractResult.email_id == email_id).all()
  
def create_extract_result(db: Session, extract_result: schemas.ExtractResultCreate):
    db_extract_result = models.ExtractResult(**extract_result.dict())
    db.add(db_extract_result)
    db.commit()
    db.refresh(db_extract_result)
    return db_extract_result
  

## AnswerResult
def get_answer_results(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AnswerResult).offset(skip).limit(limit).all()
  
def get_answer_result(db: Session, answer_result_id: int):
    return db.query(models.AnswerResult).filter(models.AnswerResult.id == answer_result_id).first()
  
def get_answer_results_by_extract_result_id(db: Session, extract_result_id: int):
    return db.query(models.AnswerResult).filter(models.AnswerResult.extract_result_id == extract_result_id).all()

def get_answer_results_by_email_id(db: Session, email_id: int):
    return db.query(models.AnswerResult).join(models.ExtractResult).filter(models.ExtractResult.email_id == email_id).all()

def create_answer_result(db: Session, answer_result: schemas.AnswerResultCreate):
    db_answer_result = models.AnswerResult(**answer_result.model_dump())
    db.add(db_answer_result)
    db.commit()
    db.refresh(db_answer_result)
    return db_answer_result
  

## DraftResult
def get_draft_results(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DraftResult).offset(skip).limit(limit).all()
  
def get_draft_result(db: Session, draft_result_id: int):
    return db.query(models.DraftResult).filter(models.DraftResult.id == draft_result_id).first()

def get_draft_results_by_email_id(db: Session, email_id: int):
    return db.query(models.DraftResult).filter(models.DraftResult.email_id == email_id).all()
  
def create_draft_result(db: Session, draft_result: schemas.DraftResultCreate):
    db_draft_result = models.DraftResult(**draft_result.dict())
    db.add(db_draft_result)
    db.commit()
    db.refresh(db_draft_result)
    return db_draft_result
