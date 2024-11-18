#! fastapi dev
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import crud, models, schemas
from .database.create_database import SessionLocal, engine
from .Generater import Generater
from .LLM.OllamaLLM import OllamaAI
from .LLM.AnythingLLM_client import AnythingLLMClient
from datetime import datetime
from .jobs import start_job_generater, update_answer, retry_draft_email
from .endpoints_models import Feedback, NewJob, FinalDraft
from multiprocessing import Process
from constants import ANYTHING_LLM_TOKEN, ANYTHING_LLM_BASE_URL
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


ollama_client = OllamaAI('http://localhost:11434', 'llama3.2:latest')
anyllm_client = AnythingLLMClient(ANYTHING_LLM_BASE_URL, ANYTHING_LLM_TOKEN)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@app.get("/")
async def root():
    return {"message": "Hello World"}
  
@app.get("/health")
async def health():
    anything_llm_health = anyllm_client.ping_alive()
    return {"message": "Service is up and running", "anything_llm": anything_llm_health}

# emails
@app.get("/emails")
async def get_mails(db: Session = Depends(get_db)):
    try:
        emails = crud.get_emails(db)
        if not emails:
            return {"message": "No emails found", "emails": []}

        emails = []
        for email in emails:
            jobs = crud.get_jobs_by_email_id(db, email.id)
            latest_job = max(jobs, key=lambda x: x.id) if jobs else None
            emails.append({ "email": email, "job": latest_job })
        
        # sort by mail date newest first
        emails.sort(key=lambda x: x["email"].sent_at, reverse=True)
        return {"emails": emails, "message": "emails fetched successfully"}
      
    except Exception as e:
        print(e)
        return {"message": "An error occured while fetching emails"}
  

@app.post("/emails")
async def create_email(email: schemas.EmailCreate, db: Session = Depends(get_db)):
    new_email = crud.create_email(db, email)
    return {"message": "Email created successfully", "email": new_email}



@app.get("/emails/{email_id}")
async def get_email(email_id: int, db: Session = Depends(get_db)):
    email = crud.get_email(db, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="email not found")
      
    jobs = crud.get_jobs_by_email_id(db, email_id)
    latest_job = max(jobs, key=lambda x: x.id) if jobs else None
    return { "email": email, "job": latest_job }



@app.post("/emails/{email_id}/save-and-confirm")
async def save_and_confirm_email(email_id: int,  body: FinalDraft, db: Session = Depends(get_db)):
    if not email_id:
        raise HTTPException(status_code=400, detail="email ID is required")

    job_id = body.job_id
    new_answers = body.answers
    new_draft = body.draft
    workspace_name = body.workspace_name
    save_in_db = bool(body.save_in_db)
    job = crud.get_job(db, body.job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
      
    for new_answer in new_answers:
        answer = crud.get_answer_result(db, new_answer['answer_id'])
        answer.answer_text = new_answer['answer']
        crud.update_answer_result(db, answer)
    
    drafts = crud.get_draft_results_by_job_id(db, job_id)
    draft = drafts[0]
    draft.draft_body = new_draft
    crud.update_draft_result(db, draft)
    
    email = crud.get_email(db, email_id)
    email.is_read = True
    crud.update_email(db, email)
    if save_in_db:  
        anyllm_client.save_draft_in_db(workspace_name, email.id, new_draft)
    

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
      
      


 
   
@app.post("/drafts/retry")
async def retry_draft(feedback: Feedback, db: Session = Depends(get_db)):
    job_id = feedback.job_id
    if not job_id:
        raise HTTPException(status_code=400, detail="Job ID is required")
      
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
      
    drafts = crud.get_draft_results_by_job_id(db, job_id)
    if not drafts:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    draft = drafts[0]
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    generator = Generater(ollama_client, anyllm_client)
    new_draft = retry_draft_email(db, generator, draft, feedback) 
    
  
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

    email_id = body.email_id
    
    email = crud.get_email(db, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="email not found")
    
    old_jobs = crud.get_jobs_by_email_id(db, email_id)
    # if old_jobs:
    #     for job in old_jobs:
    #         if job.status != models.JobStatus.COMPLETED and job.status != models.JobStatus.FAILED:
    #             print(job.status == models.JobStatus.FAILED and job.status == models.JobStatus.COMPLETED)
    #             print(f"Job already in progress: {job}")
    #             return {"message": "Job already in progress", "job": job}

    #         if job.status == models.JobStatus.COMPLETED:
    #             return {"message": "Job already exists", "job": job}

 
    job_status = models.JobStatus.PENDING.name
    new_job = schemas.JobCreate(
      email_id=email_id,
      status=job_status,
      started_at= datetime.now(),
    )
    job = crud.create_job(db, new_job)
    workspace_slug = anyllm_client.get_workspace_slug(email.workspace_name)
    if not workspace_slug:
        return {"message": f"Workspace {email.workspace_name} not found", "job": job}

    new_thread = anyllm_client.new_thread(workspace_slug, "email-"+str(email.id))
    
    process = Process(target=start_job_generater, args=(ollama_client, anyllm_client, email_id, job.id, new_thread['slug']))
    process.start()
    
    job.process_id = process.pid
    job.slug_workspace = workspace_slug
    job.slug_thread = new_thread['slug']
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
    
    body_draft = latest_draft.draft_body
    if "Subject:" in latest_draft.draft_body:
        body_draft = "\n\n".join(latest_draft.draft_body.split("\n\n")[1:])
        
    
    answers_questions = []
    for answer in answers:
        extract_result = next((extract_result for extract_result in extract_results if extract_result.id == answer.extract_result_id), None)
        answers_questions.append({
            "question": extract_result.question_text,
            "extract": extract_result.question_text,
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


@app.post("/jobs/retry")
async def retry_job(body: NewJob, db: Session = Depends(get_db)):
    email_id = body.email_id
    email = crud.get_email(db, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")
    
    old_jobs = crud.get_jobs_by_email_id(db, email_id)
    if old_jobs:
        for job in old_jobs:
            if job.status != models.JobStatus.COMPLETED and job.status != models.JobStatus.FAILED:
                print(f"Job already in progress: {job}")
                return {"message": "Job already in progress", "job": job}

            if job.status == models.JobStatus.COMPLETED and not body.force:
                return {"message": "Job already completed", "job": job}
              
            if job.status == models.JobStatus.FAILED:
                job.status = models.JobStatus.PENDING
                crud.update_job(db, job)
                workspace_slug = anyllm_client.get_workspace_slug("second_workspace")
                new_thread = anyllm_client.new_thread(workspace_slug, "email-"+str(email.id))
                process = Process(target=start_job_generater, args=(ollama_client, anyllm_client, email_id, job.id, new_thread['slug']))
                process.start()
                job.process_id = process.pid
                job.slug_workspace = workspace_slug
                job.slug_thread = new_thread['slug']

                crud.update_job(db, job)
                return {"message": "Job restarted successfully", "job": job}
              
    raise HTTPException(status_code=404, detail="Job not found")


@app.get("/workspaces")
async def get_workspaces():
    workspaces = anyllm_client.get_all_workspaces()
    return workspaces["workspaces"]