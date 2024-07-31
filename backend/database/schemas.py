from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "PENDING"
    EXTRACTING = "EXTRACTING"
    ANSWERING = "ANSWERING"
    DRAFTING = "DRAFTING"
    EVALUATING = "EVALUATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EmailBase(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    sent_at: datetime = datetime.now()
    is_read: bool = False


class Email(EmailBase):
    id: int
    questions: List['ExtractResult'] = []
    drafts: List['DraftResult'] = []
    job: Optional['Job'] = None

    class Config:
        from_attributes = True


class EmailCreate(EmailBase):
    pass


class ExtractResultBase(BaseModel):
    question_text: str
    extracted_at: datetime = datetime.now()
    is_answered: bool = False
    category: Optional[str] = None


class ExtractResult(ExtractResultBase):
    id: int
    job_id: int
    job: Optional['Job'] = None
    answer: Optional['AnswerResult'] = None

    class Config:
        from_attributes = True

class ExtractResultCreate(ExtractResultBase):
    email_id: int
    job_id: int


class AnswerResultBase(BaseModel):
    answer_text: str
    answered_at: datetime = datetime.now()
    binary_score: Optional[int] = None
    linkert_score: Optional[int] = None
    hallucination_score: Optional[int] = None
    sources: str = "" 


class AnswerResult(AnswerResultBase):
    id: int
    extract_result_id: int
    job_id: int
    job: Optional['Job'] = None
    question: Optional[ExtractResult] = None
    class Config:
        from_attributes = True


class AnswerResultCreate(AnswerResultBase):
    extract_result_id: int
    job_id: int

class DraftResultBase(BaseModel):
    draft_body: str
    created_at: datetime
    binary_score: Optional[int] = None
    linkert_score: Optional[int] = None
    hallucination_score: Optional[int] = None


class DraftResult(DraftResultBase):
    id: int
    email_id: int
    email: Optional[Email] = None

    class Config:
        from_attributes = True
        
class DraftResultCreate(DraftResultBase):
    job_id: int
    email_id: int


class JobBase(BaseModel):
    email_id: int
    status: JobStatus
    started_at: datetime
    completed_at: Optional[datetime] = None


class Job(JobBase):
    id: int
    process_id: Optional[int] = None
    email: Optional[Email] = None
    extract_results: List[ExtractResult] = []
    answer_results: List[AnswerResult] = []

    class Config:
        from_attributes = True


class JobCreate(JobBase):
    pass


Email.model_rebuild()
ExtractResult.model_rebuild()
AnswerResult.model_rebuild()
DraftResult.model_rebuild()
Job.model_rebuild()
