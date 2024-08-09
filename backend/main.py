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
import json
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
    num_new_enquiries = 0
    try:
        new_enquiries = get_unread_enquiries()
        current_enquiries = crud.get_emails(db)
        for enquiry in new_enquiries:
            if not enquiry or not enquiry.subject:
                print("Enquiry has no subject")
                continue
          
            if any(current_enquiry.subject == enquiry.subject for current_enquiry in current_enquiries):
                print(f"Enquiry already exists: {enquiry.subject}")
                continue
              
            new_enquiry = schemas.EmailCreate(
                subject=enquiry.subject,
                body=enquiry.plain if enquiry.plain else "",
                sent_at=enquiry.date,
                is_read=False
            )
            crud.create_email(db, new_enquiry)
            num_new_enquiries += 1
            
    
        mails = []
        current_enquiries = crud.get_emails(db)
        for enquiry in current_enquiries:
            jobs = crud.get_jobs_by_email_id(db, enquiry.id)
            latest_job = max(jobs, key=lambda x: x.id) if jobs else None
            mails.append({ "mail": enquiry, "job": latest_job })
            
        return {"message": f"Refreshed {num_new_enquiries} new enquiries", "mails": mails}

    except Exception as e:
        print(e)
        return {"message": "An error occured while fetching enquiries"}

@app.get("/enquiries")
async def get_enquiries(db: Session = Depends(get_db)):
    try:
        enquiries = crud.get_emails(db)
        if not enquiries:
            return {"message": "No enquiries found", "mails": []}

        mails = []
        for enquiry in enquiries:
            jobs = crud.get_jobs_by_email_id(db, enquiry.id)
            latest_job = max(jobs, key=lambda x: x.id) if jobs else None
            mails.append({ "mail": enquiry, "job": latest_job })
        
        # sort by mail date newest first
        mails.sort(key=lambda x: x["mail"].sent_at, reverse=True)
        return {"mails": mails, "message": "Enquiries fetched successfully"}
      
    except Exception as e:
        print(e)
        return {"message": "An error occured while fetching enquiries"}
  

@app.get("/enquiries/{enquiry_id}")
async def get_enquiry(enquiry_id: int, db: Session = Depends(get_db)):
    enquiry = crud.get_email(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
      
    jobs = crud.get_jobs_by_email_id(db, enquiry_id)
    latest_job = max(jobs, key=lambda x: x.id) if jobs else None
    return { "mail": enquiry, "job": latest_job }


@app.put("/enquiries/{enquiry_id}/toggle-read")
async def mark_enquiry_as_read(enquiry_id: int, db: Session = Depends(get_db)):
    enquiry = crud.get_email(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    enquiry.is_read = not enquiry.is_read
    crud.update_email(db, enquiry)
    return {"message": "Enquiry marked as read", "enquiry": enquiry}

# Answers
@app.put("/answers/{answer_id}/review")
async def review_answer(answer_id: int, db: Session = Depends(get_db)):
    if not answer_id:
        raise HTTPException(status_code=400, detail="Answer ID is required")
      
    answer = crud.get_answer_result(db, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    extract_result = crud.get_extract_result(db, answer.extract_result_id)
    if not extract_result:
        raise HTTPException(status_code=404, detail="Extract result not found")
    
    email = crud.get_email(db, extract_result.email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    reviewer = Reviewer(ollama_client)
    review = reviewer.evaluate_answers([extract_result], [answer])
    
    
    answer.binary_score = review[answer_id]['binary_scores']["useful"]
    answer.linkert_score = review[answer_id]['linkert']
    answer.hallucination_score = review[answer_id]['hallucination']
    
    crud.update_answer_result(db, answer)
    
    return {"message": "Review completed successfully", "review": review}
  
  
  
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
                print(job.status == models.JobStatus.FAILED and job.status == models.JobStatus.COMPLETED)
                print(f"Job already in progress: {job}")
                return {"message": "Job already in progress", "job": job}

            if job.status == models.JobStatus.COMPLETED:
                return {"message": "Job already exists", "job": job}

    job_status = models.JobStatus.PENDING.name
    new_job = schemas.JobCreate(
      email_id=enquiry_id,
      status=job_status,
      started_at= datetime.now(),
    )
    job = crud.create_job(db, new_job)
    workspace_slug = anyllm_client.get_workspace_slug("General")
    new_thread = anyllm_client.new_thread(workspace_slug, "email-"+str(enquiry.id))
    
    process = Process(target=start_job_generater, args=(ollama_client, anyllm_client, enquiry_id, job.id, new_thread['slug']))
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
    
    answers_questions = []
    for answer in answers:
        extract_result = next((extract_result for extract_result in extract_results if extract_result.id == answer.extract_result_id), None)
        answers_questions.append({
            "question": extract_result.question_text,
            "extract": extract_result.extract_text,
            "problem_context": extract_result.problem_context,
            "answer": answer.answer_text,
            "question_id": extract_result.id,
            "answer_id": answer.id,
            "sources": json.loads(answer.sources) if answer.sources else [],
            "unique_sources": json.loads(answer.unique_sources) if answer.unique_sources else [],
            "scores": {
                "binary_score": answer.binary_score if isinstance(answer.binary_score, int) else None,
                "hallucination_score": answer.hallucination_score if isinstance(answer.hallucination_score, int) else None,
                "linkert_score": answer.linkert_score if isinstance(answer.linkert_score, int) else None
            }
        })

    other_jobs = crud.get_jobs_by_email_id(db, job.email_id)

    extracts_to_highlight = [answer_question['extract'] for answer_question in answers_questions]
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
        "jobs": other_jobs,
        "extracts_to_highlight": extracts_to_highlight
    }


@app.delete("/jobs/{job_id}/cancel")
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
    
    reviewer = Reviewer(ollama_client)
    
    review = reviewer.evaluate(extract_questions, answers, draft_email[0].draft_body)
    review_answers = review['answers_score']
    review_draft = review['draft_email_score']
    
    for review_answer in review_answers.values():
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