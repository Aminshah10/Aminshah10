from sqlalchemy import Column, Integer, String, create_engine, Sequence
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class job_ads(Base):
    __tablename__ = "karbord"
    id = Column("ID", Integer, Sequence("user_id_seq"), primary_key=True)
    job_id = Column("Job_id", Integer)
    title = Column("title", String(50))
    description = Column("description", String(100))
    location = Column("location", String(50))
    employment_type = Column("employment_type", String(50))
    salary = Column("salary", Integer)
    resume = Column("resume", String(100))
    skills = Column("skills", String(100))
    degree = Column("degree", String(100))

    def __init__(self, title=None, job_id=None, description=None, location=None, employment_type=None, salary=None, resume=None, skills=None, degree=None):
        self.title = title
        self.job_id = job_id
        self.description = description
        self.location = location
        self.employment_type = employment_type
        self.salary = salary
        self.resume = resume
        self.skills = skills
        self.degree = degree

engine = create_engine("sqlite:///job_ads.db", echo=True)

Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind = engine)
session = Session()
