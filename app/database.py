import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL= os.getenv('DB_URL')
print(f"SQLALCHEMY_DATABASE_URL: {SQLALCHEMY_DATABASE_URL}")  # Debugging line

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")

if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("No DB_URL set for SQLAlchemy")

if not ACCESS_TOKEN_EXPIRE_MINUTES:
    raise ValueError("No ACCESS_TOKEN_EXPIRE_MINUTES set")

# Convert ACCESS_TOKEN_EXPIRE_MINUTES to an integer
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)



engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
   db = SessionLocal()
   try:
        yield db
   finally:
        db.close()
        

def init_db():
    Base.metadata.create_all(bind=engine)

