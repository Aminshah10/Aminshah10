import requests
import json
import os
import time
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, create_engine, Sequence
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class job_ads(Base):
    __tablename__ = "jobvision"
    id = Column("ID", Integer,Sequence("user_id_seq"),primary_key=True)
    job_ID = Column("job_ID", Integer)
    title = Column("title", String(50))
    description = Column("description", String(300))
    location = Column("location", String(50))
    employment_type = Column("employment_type", String(50))
    salary = Column("salary", Integer)
    resume = Column("resume", String(100))
    skills = Column("skills", String(100))
    degree = Column("degree", String(100))

    def __init__(self,job_ID=None ,title=None, description=None, location=None, employment_type=None, salary=None, resume=None, skills=None, degree=None):
        self.job_ID = job_ID
        self.title = title
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

def add_ad(job_id ,job_title, job_salary, job_resume, job_description, skills_text, job_location, employment_type, job_degree):
        existing_ad = session.query(job_ads).filter_by(job_ID=job_id).first()
        if existing_ad is None:
            new_ad = job_ads(
                job_ID = job_id,
                title=job_title,
                salary = job_salary,
                resume = job_resume,
                description = job_description,
                skills = skills_text,
                location = job_location,
                employment_type = employment_type,
                degree = job_degree)                
            session.add(new_ad)
            session.commit()

def safe_get(dictionary, *keys, default=""):
    current = dictionary
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default if key == keys[-1] else {})
        else:
            return default
    return current

def clean_html_text(html_text):
    if html_text:
        soup = BeautifulSoup(html_text, 'html.parser')
        return soup.get_text(separator=' ').strip()
    return ""

url = "https://candidateapi.jobvision.ir/api/v1/JobPost/List"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Content-Type": "application/json",
}

job_ids = []

for page in range(1,2):
    payload = {
        "jobCategoryUrlTitle": "developer",
        "pageSize": 30,
        "requestedPage": page,
        "sortBy": 0,
        "searchId": None
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        
        with open(f"jobvision_jobs{page}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            job_posts = data["data"]["jobPosts"]
            
            for job in job_posts:
                job_id = job.get("id")
                job_ids.append(job_id)
        os.remove(f"jobvision_jobs{page}.json")
    time.sleep(3)


for job_id in job_ids:
    url= f"https://candidateapi.jobvision.ir/api/v1/JobPost/Detail?jobPostId={str(job_id)}"

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
            data = response.json()
            with open(f"jobvision_job{job_id}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            skills = []
            software_reqs = safe_get(data, "data", "softwareRequirements", default=[])
            if software_reqs is None:
                software_reqs = []
            for req in software_reqs:
                software_title = safe_get(req, "software", "titleFa", default="")
                skill_level = safe_get(req, "skill", "titleFa", default="")
                if software_title and skill_level:
                    skill_str = f"{software_title} {skill_level}"
                    skills.append(skill_str)

            language_reqs = safe_get(data, "data", "languageRequirements", default=[])
            if language_reqs is None:
                language_reqs = []
            for lang in language_reqs:
                language_title = safe_get(lang, "language", "titleFa", default="")
                lang_skill = safe_get(lang, "skill", "titleFa", default="")
                if language_title and lang_skill:
                    lang_str = f"{language_title} {lang_skill}"
                    skills.append(lang_str)

            job_title = safe_get(data, "data", "title", default="")
            job_salary = safe_get(data, "data", "salary", "titleFa", default=None)
            job_description = clean_html_text(safe_get(data, "data", "description", default= None))
            job_skills = str(' '.join(skills))
            job_location = safe_get(data, "data", "location", "city", "titleFa", default= "")+" "+safe_get(data, "data", "location", "region", "titleFa", default="") if safe_get(data, "data", "location", "city", "titleFa", default= "")+" "+safe_get(data, "data", "location", "region", "titleFa", default="") != " " else None
            job_employment_type = safe_get(data, "data", "workType", "titleFa", default=None)
            job_degree = safe_get(data,"data","seniorityLevel","titleFa", default=None)
            
            os.remove(f"jobvision_job{job_id}.json")
            
            url2 = f"https://candidateapi.jobvision.ir/api/v1/JobPost/GetMatchConfiguration?jobPostId={str(job_id)}"
            headers2 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json",
            }
            response2 = requests.get(url2, headers=headers2)
            data2 = response2.json()
            with open(f"jobvision_job{job_id}.json", "w", encoding="utf-8") as f:
                json.dump(data2, f, ensure_ascii=False, indent=4)
            
            job_resume = safe_get(data2,"data","scoreOfWorkExperienceInJobCategory","expectedValue",default=None)
            add_ad(job_id,job_title,job_salary,job_resume,job_description,job_skills,job_location,job_employment_type,job_degree)
            
            os.remove(f"jobvision_job{job_id}.json")
    
    time.sleep(3)
