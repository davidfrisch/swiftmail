from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class AnswerResultBase(BaseModel):
    extract_result_id: int
    answer_text: str
    answered_at: datetime
    binary_score: Optional[int] = None
    linkert_score: Optional[int] = None
    hallucination_score: Optional[int] = None

class AnswerResultCreate(AnswerResultBase):
    pass

class AnswerResult(AnswerResultBase):
    id: int

    class Config:
        from_attributes = True


class ExtractResultBase(BaseModel):
    email_id: int
    question_text: str
    extracted_at: datetime
    is_answered: bool
    category: Optional[str] = None

class ExtractResultCreate(ExtractResultBase):
    pass

class ExtractResult(ExtractResultBase):
    id: int
    answers: List[AnswerResult] = []

    class Config:
        from_attributes = True


class DraftResultBase(BaseModel):
    draft_body: str
    created_at: datetime
    binary_score: Optional[int] = None
    linkert_score: Optional[int] = None
    hallucination_score: Optional[int] = None

class DraftResultCreate(DraftResultBase):
    pass

class DraftResult(DraftResultBase):
    id: int
    email_id: int

    class Config:
        from_attributes = True


class EmailBase(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    sent_at: datetime
    is_read: bool

class EmailCreate(EmailBase):
    pass

class Email(EmailBase):
    id: int
    questions: List[ExtractResult] = []
    drafts: List[DraftResult] = []

    class Config:
        from_attributes = True


class JobBase(BaseModel):
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    email_id: int


class Job(JobBase):
    id: int
    process_id: Optional[int] = None

    class Config:
        from_attributes = True

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    process_id: Optional[int] = None

    class Config:
        from_attributes = True