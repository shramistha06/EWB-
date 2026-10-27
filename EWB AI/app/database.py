from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# New file name so it never clashes with the old project's students.db
DATABASE_URL = "sqlite:///./edumentor.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
