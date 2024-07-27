#! fastapi dev
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from .database import crud, models, schemas
from .database.create_database import SessionLocal, engine
from .email_client.gmail import get_unread_enquiries
import time
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
        
    return {"message": f"Found {len(new_enquiries)} new enquiries"}


@app.get("/enquiries")
async def get_enquiries(db: Session = Depends(get_db)):
    enquiries = crud.get_extract_results(db)
    if not enquiries:
        raise HTTPException(status_code=404, detail="No enquiries found")
    return enquiries
  
