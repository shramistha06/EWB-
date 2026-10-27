from sqlalchemy import Column, Integer, String, Float
from .database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    course = Column(String, nullable=False)
    marks = Column(Float, default=0.0)          # out of 100
    attendance = Column(Float, default=0.0)     # percentage
    skills = Column(String, default="")         # comma separated
