from pydantic import BaseModel
from typing import List

class Feedback(BaseModel):
    feedback: str
    
class NewJob(BaseModel):
    email_id: int

class FinalDraft(BaseModel):
    job_id: int
    answers: List[dict]
    draft: str
    save_in_db: bool = False