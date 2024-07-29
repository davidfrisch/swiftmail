from pydantic import BaseModel

class Feedback(BaseModel):
    feedback: str
    
class NewJob(BaseModel):
    email_id: int