from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import quote
from dotenv import load_dotenv
from pathlib import Path
import os;


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

db_url = os.getenv('DB_URL')

engine=create_engine(db_url)

SessionLocal=sessionmaker(bind=engine,expire_on_commit=False)

Base=declarative_base()