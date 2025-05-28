import re
from rapidfuzz import fuzz, utils
from typing import List, Dict, Tuple
from dataclasses import dataclass
import re
import statistics
import sqlite3
from sqlalchemy import Column, Integer, String, create_engine, Sequence
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Similars(Base):
    __tablename__ = "similar_jobs"
    id = Column("ID", Integer, Sequence("user_id_seq"), primary_key=True)
    Job_id = Column("Job_id", Integer)
    similars = Column("title", String(300))


    def __init__(self, similars=None, Job_id=None):
        self.similars = similars
        self.Job_id = Job_id


engine = create_engine("sqlite:///similar_jobs.db", echo=True)

Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind = engine)
session = Session()

def add_ad(Job_id ,job_similars):
        existing_job = session.query(Similars).filter_by(Job_id=Job_id).first()
        if existing_job is None:
            new_ad = Similars(
                Job_id = Job_id,
                similars=job_similars
                )                
            session.add(new_ad)
            session.commit()
@dataclass
class Job:
    id: int
    site: str
    title: str
    description: str
    skills: str
    job_type: str
    location: str
    salary: str
    min_experience: str
    min_education: str

class JobSimilarityEngine:
    def __init__(self, job_posts: List[Job]):
        self.job_posts = job_posts
        self.field_weights = {
            'title': 0.3,
            'description': 0.2,
            'skills': 0.3,
            'job_type': 0.05,
            'location': 0.05,
            'salary': 0.05,
            'min_experience': 0.025,
            'min_education': 0.025
        }
        self.cache = {}

    def preprocess_text(self, text: str) -> str:
        if not text:
            return ""
        text = utils.default_process(text)
        text = re.sub(r'\s+', ' ', text.strip())
        replacements = {"پاره وقت": "نیمه وقت", "دورکاری": "کار از خانه", "کارشناسی": "لیسانس", "ارشد": "فوق لیسانس"}
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text

    def calculate_field_similarity(self, field: str, value1: str, value2: str) -> float:
        if not value1 or not value2:
            return 0.0
        key = (field, value1, value2)
        if key in self.cache:
            return self.cache[key]
        value1, value2 = self.preprocess_text(value1), self.preprocess_text(value2)
        if field in ['title', 'skills']:
            similarity = fuzz.token_set_ratio(value1, value2) / 100
        elif field == 'description':
            similarity = (fuzz.ratio(value1, value2) * 0.6 + fuzz.partial_ratio(value1, value2) * 0.4) / 100
        elif field == 'job_type':
            similarity = 1.0 if value1 == value2 else 0.0
        elif field == 'location':
            similarity = fuzz.token_set_ratio(value1, value2) / 100
        else:
            similarity = 0.0
        self.cache[key] = similarity
        return similarity

    def calculate_job_similarity(self, job1: Job, job2: Job) -> Tuple[float, str]:
        total_similarity = sum(
            self.calculate_field_similarity(field, getattr(job1, field), getattr(job2, field)) * weight
            for field, weight in self.field_weights.items()
        )
        return round(total_similarity * 100, 2), job2.site    
    
    def find_similar_jobs(self, target_job: Job, threshold: float = 70.0, top_n: int = 5) -> List[Tuple[Job, float, str]]:
        similarities = [
            (job, *self.calculate_job_similarity(target_job, job))
            for job in self.job_posts if job.id != target_job.id
        ]
        return sorted(similarities, key=lambda x: x[1], reverse=True)[:top_n]

class Job:
    def __init__(self, id, site, title, description, skills, job_type="programming", location="", salary="", min_experience="", min_education=""):
        self.id = id
        self.site = site
        self.title = title
        self.description = description
        self.skills = skills
        self.job_type = job_type
        self.location = location
        self.salary = salary
        self.min_experience = min_experience
        self.min_education = min_education

def extract_experience(resume_text):
    if not resume_text:
        return 0
    persian_to_english = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    resume_text = resume_text.translate(persian_to_english)
    numbers = list(map(int, re.findall(r'\d+', resume_text)))
    if not numbers:
        return 0
    elif len(numbers) == 1:
        return numbers[0]
    else:
        return round(statistics.mean(numbers))

conn = sqlite3.connect('job_ads.db')
cursor = conn.cursor()

running = True
while running:
    input_id = input()
    if not input_id.isdigit():
        print("wrong id")
        continue
    input_id = int(input_id)
    input_str = str(input_id)
    target_job = None
    job_posts = []
    
    if len(input_str) == 7:
        # پیدا کردن شغل هدف از jobvision
        cursor.execute("SELECT Job_id, title, description, location, employment_type, salary, resume, skills, degree FROM jobvision WHERE Job_id = ?", (input_id,))
        result = cursor.fetchone()
        if result:
            target_job = Job(
                id=result[0],
                site="jobvision",
                title=result[1] or "",
                description=result[2] or "",
                skills=result[7] or "",
                job_type=result[4] or "programming",
                location=result[3] or "",
                salary=result[5] or "",
                min_experience=str(extract_experience(result[6])) if result[6] else "",
                min_education=result[8] or ""
            )
            # گرفتن بقیه شغل‌ها از karbord
            cursor.execute("SELECT Job_id, title, description, location, employment_type, salary, resume, skills, degree FROM karbord")
            for row in cursor.fetchall():
                job = Job(
                    id=row[0],
                    site="karbord",
                    title=row[1] or "",
                    description=row[2] or "",
                    skills=row[7] or "",
                    job_type=row[4] or "programming",
                    location=row[3] or "",
                    salary=row[5] or "",
                    min_experience=str(extract_experience(row[6])) if row[6] else "",
                    min_education=row[8] or ""
                )
                job_posts.append(job)
            running = False
        else:
            print("wrong id")
    elif len(input_str) == 8:
        # پیدا کردن شغل هدف از karbord
        cursor.execute("SELECT Job_id, title, description, location, employment_type, salary, resume, skills, degree FROM karbord WHERE Job_id = ?", (input_id,))
        result = cursor.fetchone()
        if result:
            target_job = Job(
                id=result[0],
                site="karbord",
                title=result[1] or "",
                description=result[2] or "",
                skills=result[7] or "",
                job_type=result[4] or "programming",
                location=result[3] or "",
                salary=result[5] or "",
                min_experience=str(extract_experience(result[6])) if result[6] else "",
                min_education=result[8] or ""
            )
            # گرفتن بقیه شغل‌ها از jobvision
            cursor.execute("SELECT Job_id, title, description, location, employment_type, salary, resume, skills, degree FROM jobvision")
            for row in cursor.fetchall():
                job = Job(
                    id=row[0],
                    site="jobvision",
                    title=row[1] or "",
                    description=row[2] or "",
                    skills=row[7] or "",
                    job_type=row[4] or "programming",
                    location=row[3] or "",
                    salary=row[5] or "",
                    min_experience=str(extract_experience(row[6])) if row[6] else "",
                    min_education=row[8] or ""
                )
                job_posts.append(job)
            running = False
        else:
            print("wrong id")
    else:
        print("wrong id")

conn.close()

similars = []
# تست الگوریتم
if target_job and job_posts:
    engine = JobSimilarityEngine(job_posts)
    similar_jobs = engine.find_similar_jobs(target_job)
    for job, similarity, site in similar_jobs:
        similars.append(f"job id : {job.id} - similarity percentage: {similarity:.2f}%")

add_ad(input_id," ".join(similars))