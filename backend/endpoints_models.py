from pydantic import BaseModel
from typing import List

class Feedback(BaseModel):
    feedback: str
    job_id: int = None
    
class NewJob(BaseModel):
    email_id: int
    workspace_name: str
    force: bool = False

class FinalDraft(BaseModel):
    job_id: int
    answers: List[dict]
    draft: str
    save_in_db: bool = False