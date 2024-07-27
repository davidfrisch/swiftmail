from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    subject = Column(String(255), nullable=True)
    body = Column(String, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    
    questions = relationship("ExtractResult", back_populates="email")
    drafts = relationship("DraftResult", back_populates="email")

    def __repr__(self):
        return f"<Email(id={self.id} " \
               f"subject={self.subject}, sent_at={self.sent_at}, is_read={self.is_read})>"


class ExtractResult(Base):
    __tablename__ = 'extract_results'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    question_text = Column(String, nullable=False)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    is_answered = Column(Boolean, default=False)
    category = Column(String, nullable=True)
    
    email = relationship("Email", back_populates="questions")
    answers = relationship("AnswerResult", secondary='draft_answer_link', back_populates="drafts")

    def __repr__(self):
        return f"<ExtractResult(id={self.id}, email_id={self.email_id}, " \
               f"question_text={self.question_text}, extracted_at={self.extracted_at}, category={self.category}, " \
               f"is_answered={self.is_answered})>"
               


class AnswerResult(Base):
    __tablename__ = 'answer_results'

    id = Column(Integer, primary_key=True)
    extract_result_id = Column(Integer, ForeignKey('extract_results.id'), nullable=False)
    answer_text = Column(String, nullable=False)
    answered_at = Column(DateTime, default=datetime.now())
    binary_score = Column(Integer, nullable=True)
    linkert_score = Column(Integer, nullable=True)
    hallucination_score = Column(Integer, nullable=True)

    question = relationship("ExtractResult", back_populates="answer")

    def __repr__(self):
        return f"<AnswerResult(id={self.id}, extract_result_id={self.extract_result_id}, " \
               f"answer_text={self.answer_text}, answered_at={self.answered_at})>"
               
               
class DraftResult(Base):
    __tablename__ = 'draft_results'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    draft_body = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    binary_score = Column(Integer, nullable=True)
    linkert_score = Column(Integer, nullable=True)
    hallucination_score = Column(Integer, nullable=True)

    email = relationship("Email", back_populates="drafts")

    def __repr__(self):
        return f"<DraftResult(id={self.id}, email_id={self.email_id}, " \
               f"draft_body={self.draft_body}, created_at={self.created_at})>"