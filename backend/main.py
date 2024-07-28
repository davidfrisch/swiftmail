#! fastapi dev
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from .database import crud, models, schemas
from .database.create_database import SessionLocal, engine
from .email_client.gmail import get_unread_enquiries
from .Generater import Generater
from .LLM.OllamaLLM import OllamaAI
from .LLM.AnythingLLM_client import AnythingLLMClient
from datetime import datetime
from .jobs import start_job_generater, update_answer, update_draft_email
from .endpoints_models import Feedback
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
ollama_client = OllamaAI('http://localhost:11434', 'llama3:instruct')
anyllm_client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/enquiries/refresh")
async def refresh_enquiries(db: Session = Depends(get_db)):
    new_enquiries = get_unread_enquiries()
    for enquiry in new_enquiries:
        new_enquiry = schemas.EmailCreate(
            subject=enquiry.subject,
            body=enquiry.plain if enquiry.plain else "",
            sent_at=enquiry.date,
            is_read=False
        )
        crud.create_email(db, new_enquiry)
        
    enquiries = crud.get_emails(db)
    return {"message": f"Found {len(new_enquiries)} new enquiries", "enquiries": enquiries}


@app.get("/enquiries")
async def get_enquiries(db: Session = Depends(get_db)):
    enquiries = crud.get_emails(db)
    if not enquiries:
        raise HTTPException(status_code=404, detail="No enquiries found")
    return enquiries
  

@app.get("/enquiries/{enquiry_id}")
async def get_enquiry(enquiry_id: int, db: Session = Depends(get_db)):
    enquiry = crud.get_email(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    return enquiry

@app.get("/enquiries/{enquiry_id}/results")
async def get_enquiry_results(enquiry_id: int, db: Session = Depends(get_db)):
    enquiry = crud.get_email(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    
    extract_results = crud.get_extract_results_by_email_id(db, enquiry_id)
    answers = crud.get_answer_results_by_email_id(db, enquiry_id)
    draft_result = crud.get_draft_results_by_email_id(db, enquiry_id)
    
    return {
        "extract_results": extract_results,
        "answers": answers,
        "draft_result": draft_result
    }

@app.post("/enquiries/{enquiry_id}/generate-response")
async def generate_response(enquiry_id: int, db: Session = Depends(get_db)):
    if not enquiry_id:
        raise HTTPException(status_code=400, detail="Enquiry ID is required")
  
    enquiry = crud.get_email(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    
    generator = Generater(ollama_client, anyllm_client)
    job_status = models.JobStatus.PENDING.name
    new_job = schemas.JobCreate(
      email_id=enquiry_id,
      status=job_status,
      started_at= datetime.now(),
    )
    job = crud.create_job(db, new_job)
    
    results = start_job_generater(db, generator, enquiry, job)

    return {"message": "Response generated successfully", "results": results}



@app.post("/answers/{answer_id}")
async def retry_answer(answer_id: int, feedback: Feedback, db: Session = Depends(get_db)):
    if not answer_id:
        raise HTTPException(status_code=400, detail="Answer ID is required")
      
    answer = crud.get_answer_result(db, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    generator = Generater(ollama_client, anyllm_client)
    new_answer = update_answer(db, generator, answer, feedback)
  
    return {"message": "Answer updated successfully", "answer": new_answer}
      
      
    
@app.post("/drafts/{draft_id}")
async def retry_draft(draft_id: int, feedback: Feedback, db: Session = Depends(get_db)):
    if not draft_id:
        raise HTTPException(status_code=400, detail="Draft ID is required")
      
    draft = crud.get_draft_result(db, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    generator = Generater(ollama_client, anyllm_client)
    new_draft = update_draft_email(db, generator, draft, feedback) 
  
    return {"message": "Draft updated successfully", "draft": new_draft} 