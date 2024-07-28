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
from .jobs import start_job_generater
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
  

@app.post("/enquiries/{enquiry_id}/generate-response")
async def generate_response(enquiry_id: int, db: Session = Depends(get_db)):
    if not enquiry_id:
        raise HTTPException(status_code=400, detail="Enquiry ID is required")
  
    enquiry = crud.get_email(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    
    ollama_client = OllamaAI('http://localhost:11434', 'llama3:instruct')
    anyllm_client = AnythingLLMClient("http://localhost:3001/api", "3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF")

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
