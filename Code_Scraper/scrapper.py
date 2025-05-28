from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from sqlalchemy import Column, Integer, String, create_engine, Sequence
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class job_ads(Base):
    __tablename__ = "ads"
    id = Column("ID", Integer, Sequence("user_id_seq"), primary_key=True)
    title = Column("title", String(50))
    description = Column("description", String(100))
    location = Column("location", String(50))
    employment_type = Column("employment_type", String(50))
    salary = Column("salary", Integer)
    resume = Column("resume", String(100))
    skills = Column("skills", String(100))
    degree = Column("degree", String(100))

    def __init__(self,title=None, description=None, location=None, employment_type=None, salary=None, resume=None, skills=None, degree=None):
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


options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--start-maximized")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("window-size=1920,1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
job_cleaned = []

for i in range(1,3):
    page_link = f"https://jobvision.ir/jobs/category/developer?page={i}&sort=1"
    driver.get(page_link)

    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "job-card"))
    )

    job_links = driver.find_elements(By.CSS_SELECTOR, "job-card a[href]")
    
    for i, link in enumerate(job_links, 1):
        href_value = link.get_attribute("href")
        if "companies" in href_value or "category" in href_value:
            pass
        else:
            job_cleaned.append(href_value)

    time.sleep(5)


for i in range(20):
    try:
        driver.get(job_cleaned[i])
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.container"))
        )
        try:
            job_title = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".job-title"))
            ).text
            # print(f"title: {job_title}")
        except:
            try:
                job_title = WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located((By.TAG_NAME, "h1"))
                ).text
                # print(f"title: {job_title}")
            except:
                pass
        try:
            job_salary = driver.find_element(By.CLASS_NAME, "yn_price").text
            # print(f"salary: {job_salary}")
        except:
            pass
        try:
            job_resume = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".col.mr-2.px-0.word-break"))
            ).text
            # print(f"resume: {job_resume}")
        except:
            pass
        try:
            description_container = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.col.px-0.mr-2"))
            )
            job_description = description_container.text.strip()
            # print(f"description: {job_description}")
        except:
            pass
        try:
            skills_text = []
            skills_container = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".row.col-11.px-0"))
            )
            skills = skills_container.find_elements(By.CSS_SELECTOR, "span.d-flex.bg-white.text-black.border.border-secondary.col.rounded-sm.text-white")
            skills_text.extend([skill.text for skill in skills if skill.text.strip()])
            additional_skills = driver.find_elements(By.CSS_SELECTOR, "div.col-12.mb-3.pr-0 span.col.mr-2.px-0.word-break")
            skills_text.extend([skill.text for skill in additional_skills if skill.text.strip() and "سابقه کار" not in skill.text])
            if skills_text:
                skills_text = str(skills_text)
        except:
            pass
        try:
            job_location = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".yn_category"))
            ).text
            # print(f"location: {job_location}")
        except:
            try:
                location_container = WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "div.yn_category"))
                )
                job_location = location_container.text.strip()
                # print(f"location: {job_location}")
            except:
                pass
        try:
            parent_div = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//div[.//div[text()='نوع همکاری']]"))
            )
            child_divs = parent_div.find_elements(By.TAG_NAME, "div")
            if len(child_divs) >= 2:
                employment_type = child_divs[1].text
                # print(f"employment_type: {employment_type}")
        except:
            try:
                employment_type = WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(text(), 'تمام وقت') or contains(text(), 'پاره وقت') or contains(text(), 'دورکاری')]"))
                ).text
                # print(f"employment_type: {employment_type}")
            except:
                pass
    except:
        pass
    print("---------------------------------------------------------------------")
    def add_ad(job_title, job_salary, job_resume, job_description, skills_text, job_location, employment_type):
        new_ad = job_ads(
            title=job_title,
            salary = job_salary,
            resume = job_resume,
            description = job_description,
            skills = skills_text,
            location = job_location,
            employment_type = employment_type,
            degree = None)
            
        session.add(new_ad)
        session.commit()
    add_ad(job_title, job_salary, job_resume, job_description, skills_text, job_location, employment_type)

driver.quit()
