from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from .create_database import Base
import enum

class JobStatus(enum.Enum):
    PENDING = "PENDING"
    EXTRACTING = "EXTRACTING"
    ANSWERING = "ANSWERING"
    DRAFTING = "DRAFTING"
    EVALUATING = "EVALUATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    subject = Column(String(255), nullable=True)
    body = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    
    questions = relationship("ExtractResult", back_populates="email")
    drafts = relationship("DraftResult", back_populates="email")
    job = relationship("Job", uselist=False, back_populates="email")

    def __repr__(self):
        return f"<Email(id={self.id}, subject={self.subject}, body={self.body})>"

class ExtractResult(Base):
    __tablename__ = 'extract_results'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False) 
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)  
    question_text = Column(String, nullable=False)
    problem_context = Column(String, nullable=True)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    is_answered = Column(Boolean, default=False)
    category = Column(String, nullable=True)
    
    email = relationship("Email", back_populates="questions")
    job = relationship("Job", back_populates="extract_results")
    answer = relationship("AnswerResult", uselist=False, back_populates="question")

    def __repr__(self):
        return f"<ExtractResult(id={self.id}, email_id={self.email_id}, " \
               f"question_text={self.question_text}, extracted_at={self.extracted_at}, category={self.category}, " \
               f"is_answered={self.is_answered})>"

class AnswerResult(Base):
    __tablename__ = 'answer_results'

    id = Column(Integer, primary_key=True)
    extract_result_id = Column(Integer, ForeignKey('extract_results.id'), nullable=False)
    sources = Column(Text, nullable=True)
    unique_sources = Column(Text, nullable=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)  # Corrected table name
    answer_text = Column(String, nullable=False)
    answered_at = Column(DateTime, default=datetime.now())
    binary_score = Column(Integer, nullable=True)
    linkert_score = Column(Integer, nullable=True)
    hallucination_score = Column(Integer, nullable=True)

    question = relationship("ExtractResult", back_populates="answer")
    job = relationship("Job", back_populates="answer_results")

    def __repr__(self):
        return f"<AnswerResult(id={self.id}, extract_result_id={self.extract_result_id}, " \
               f"answer_text={self.answer_text}, answered_at={self.answered_at})>"

class DraftResult(Base):
    __tablename__ = 'draft_results'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    draft_body = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    binary_score = Column(Integer, nullable=True)
    linkert_score = Column(Integer, nullable=True)
    hallucination_score = Column(Integer, nullable=True)

    email = relationship("Email", back_populates="drafts")
    job = relationship("Job", back_populates="draft_results")

    def __repr__(self):
        return f"<DraftResult(id={self.id}, email_id={self.email_id}, " \
               f"draft_body={self.draft_body}, created_at={self.created_at})>"

class Job(Base):
    __tablename__ = 'jobs'  # Ensure this matches the foreign key references

    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, nullable=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    started_at = Column(DateTime, default=datetime.now())
    completed_at = Column(DateTime, nullable=True)
    slug_workspace = Column(String, nullable=True)
    slug_thread = Column(String, nullable=True)

    email = relationship("Email", back_populates="job")
    extract_results = relationship("ExtractResult", back_populates="job")
    answer_results = relationship("AnswerResult", back_populates="job")
    draft_results = relationship("DraftResult", back_populates="job")
    
    def __repr__(self):
        return f"<Job(id={self.id}, email_id={self.email_id}, status={self.status}, " \
               f"started_at={self.started_at}, completed_at={self.completed_at})>"
