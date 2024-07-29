from database import SessionLocal
from fastapi import Depends
from sqlalchemy.orm import Session

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_db_session(session: Session = Depends(get_session)):
    return session
