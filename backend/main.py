#! fastapi dev
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import crud, models, schemas
from .database.create_database import SessionLocal, engine
from .email_client.gmail import get_unread_enquiries
from .Generater import Generater
from .Reviewer import Reviewer
from .LLM.OllamaLLM import OllamaAI
from .LLM.AnythingLLM_client import AnythingLLMClient
from datetime import datetime
from .jobs import start_job_generater, update_answer, update_draft_email
from .endpoints_models import Feedback, NewJob
from multiprocessing import Process
import os, signal
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

# Enquiries

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
    
    mails = []
    for enquiry in new_enquiries:
        job = crud.get_jobs_by_email_id(db, enquiry.id)
        mails.append({ "mail": enquiry, "job": job[0] if job else None })
        
    return {"message": f"Found {len(new_enquiries)} new enquiries", "mails": mails}


@app.get("/enquiries")
async def get_enquiries(db: Session = Depends(get_db)):
    enquiries = crud.get_emails(db)
    if not enquiries:
        raise HTTPException(status_code=404, detail="No enquiries found")

    mails = []
    for enquiry in enquiries:
        jobs = crud.get_jobs_by_email_id(db, enquiry.id)
        job = jobs[0] if jobs else None
        mails.append({ "mail": enquiry, "job": job })
            
    return mails
  

@app.get("/enquiries/{enquiry_id}")
async def get_enquiry(enquiry_id: int, db: Session = Depends(get_db)):
    enquiry = crud.get_email(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
      
    jobs = crud.get_jobs_by_email_id(db, enquiry_id)
    
    return { "mail": enquiry, "job": jobs[0] if jobs else None }


@app.put("/enquiries/{enquiry_id}/toggle-read")
async def mark_enquiry_as_read(enquiry_id: int, db: Session = Depends(get_db)):
    enquiry = crud.get_email(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    enquiry.is_read = not enquiry.is_read
    crud.update_email(db, enquiry)
    return {"message": "Enquiry marked as read", "enquiry": enquiry}

# Answers

@app.put("/answers/{answer_id}")
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
  

# Jobs

@app.get("/jobs")
async def get_jobs(db: Session = Depends(get_db)):
    jobs = crud.get_jobs(db)
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found")
      
      
    for job in jobs:
        email = crud.get_email(db, job.email_id)
        job.email = email
        
    return jobs


@app.post("/jobs")
async def generate_response(body: NewJob, db: Session = Depends(get_db)):

    enquiry_id = body.email_id
    enquiry = crud.get_email(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    
    old_jobs = crud.get_jobs_by_email_id(db, enquiry_id)
    if old_jobs:
        for job in old_jobs:
            if job.status != models.JobStatus.COMPLETED and job.status != models.JobStatus.FAILED:
                print(models.JobStatus.COMPLETED)
                print(f"Job already in progress: {job}")
                return {"message": "Job already in progress", "job": job}

            return {"message": "Job already exists", "job": job}

    job_status = models.JobStatus.PENDING.name
    new_job = schemas.JobCreate(
      email_id=enquiry_id,
      status=job_status,
      started_at= datetime.now(),
    )
    job = crud.create_job(db, new_job)
    
    process = Process(target=start_job_generater, args=(ollama_client, anyllm_client, enquiry_id, job.id))
    process.start()
    
    job.process_id = process.pid
    print(f"Process started with PID: {process.pid}")
    crud.update_job(db, job)

    return {"message": "Response generated successfully", "job": job}

  
@app.get("/jobs/{job_id}/results")
async def get_jobs_results(job_id: int, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    email = crud.get_email(db, job.email_id)
    extract_results = crud.get_extract_results_by_job_id(db, job_id)
    answers = crud.get_answer_results_by_job_id(db, job_id)
    draft_result = crud.get_draft_results_by_job_id(db, job_id)
    latest_draft = draft_result[0]
    subject_draft = latest_draft.draft_body.split("\n\n")[0]
    body_draft = "\n\n".join(latest_draft.draft_body.split("\n\n")[1:])
    
    
    answers_questions = [{
      "question" : next((extract.question_text for extract in extract_results if extract.id == answer.extract_result_id), None),
      "answer" : answer.answer_text,
      "question_id" : answer.extract_result_id,
      "answer_id" : answer.id,
      "scores": {
        "binary_score": answer.binary_score if answer.binary_score else None,
        "hallucination_score": answer.hallucination_score if answer.hallucination_score else None, 
        "linkert_score": answer.linkert_score if answer.linkert_score else None
      }
    } for answer in answers]

    other_jobs = crud.get_jobs_by_email_id(db, job.email_id)
    
    return {
        "email": email,
        "extract_results": extract_results,
        "answers": answers,
        "draft_result": {
            "subject": subject_draft,
            "body": body_draft,
            "created_at": latest_draft.created_at,
        },
        "answers_questions": answers_questions,
        "jobs": other_jobs
    }


@app.put("/jobs/{job_id}/cancel")
async def cancel_job(job_id: int, db: Session = Depends(get_db)):
    if not job_id:
        raise HTTPException(status_code=400, detail="Job ID is required")
      
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status == models.JobStatus.FAILED or job.status == models.JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job already completed or failed")
    
    job.status = models.JobStatus.FAILED
    
    try:
        if job.process_id:
            os.kill(job.process_id, signal.SIGTERM)
            print(f"Process with PID {job.process_id} killed")
    except ProcessLookupError:
        print(f"Process with PID {job.process_id} not found")
    crud.update_job(db, job)
    
    return {"message": "Job cancelled successfully", "job": job_id}


# Reviewer
@app.get("/reviewer/{job_id}")
async def review_job(job_id: int, db: Session = Depends(get_db)):
    if not job_id:
        raise HTTPException(status_code=400, detail="Job ID is required")
      
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    email = crud.get_email(db, job.email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
      
    extract_questions = crud.get_extract_results_by_job_id(db, job_id)
    answers = crud.get_answer_results_by_job_id(db, job_id)
    draft_email = crud.get_draft_results_by_job_id(db, job_id)
    
    reviewer = Reviewer(ollama_client, extract_questions, answers, draft_email)
    
    review = reviewer.evaluate()
    review_answers = review['answers']
    review_draft = review['draft_email']
    
    for review_answer in review_answers:
        answer = crud.get_answer_result(db, review_answer['answer_id'])
        answer.binary_score = review_answer['binary_scores']["useful"]
        answer.linkert_score = review_answer['linkert']
        answer.hallucination_score = review_answer['hallucination']
        crud.update_answer_result(db, answer)
    
    draft = draft_email[0]
    draft.binary_score = review_draft['binary_scores']["useful"]
    draft.linkert_score = review_draft['linkert']
    draft.hallucination_score = review_draft['hallucination']
    crud.update_draft_result(db, draft)
    
    
    
    return {"message": "Review completed successfully", "job": job_id}