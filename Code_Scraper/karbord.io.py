import requests
import json
import time
import os
import unicodedata
from typing import List, Dict
import re
from bs4 import BeautifulSoup
from database import job_ads,session


url = "https://api.karbord.io/api/v1/Candidate/JobPost/GetList"
job_ids = []
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36",
    "Content-Type": "application/json; charset=utf-8",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "clientid": "4769806",
    "ngsw-bypass": "true",
    "origin": "https://karbord.io",
    "referer": "https://karbord.io/",
    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "priority": "u=1, i"
}

for page in range(1, 3):
    payload = {
        "jobBoardIds": [],
        "jobPostCategories": ["all-Programming"],
        "nextPageToken": "{\"lastJobPostTime\":\"2025-05-20T09:10:13Z\"}",
        "page": page,
        "pageSize": 30,
        "searchId": "388334190922297072",
        "location": None,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            data = response.json()
            with open(f"karbord_jobs{page}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            try:
                error_details = response.json()
            except:
                pass

    except :
        pass

    try:
        with open(f"karbord_jobs{page}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            job_posts = data["data"]["jobPosts"]
            
            for job in job_posts:
                job_id = job.get("id")
                job_ids.append(job_id)

    except :
        pass
    
    time.sleep(5)
    os.remove(f"karbord_jobs{page}.json")

for id in job_ids:
    url = "https://api.karbord.io/api/v1/Candidate/JobPost/GetDetail?jobPostId=" + str(id)
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/json; charset=utf-8",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "identity",  
        "accept-language": "en-US,en;q=0.9",
        "clientid": "4769806",
        "ngsw-bypass": "true",
        "origin": "https://karbord.io",
        "referer": "https://karbord.io/",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "priority": "u=1, i"
    }

    try:
        response = requests.get(url, headers=headers)  

        if response.status_code == 200:
            data = response.json()
            with open(f"karbord_job{id}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            try:
                error_details = response.json()
            except:
                pass

    except :
        pass
    
    file_path = f"karbord_job{id}.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except :
        pass
    def clean_html(text: str) -> str:
        clean_text = re.sub(r'<[^>]+>', '', text or '')
        clean_text = re.sub(r'\n\s*\n', '\n', clean_text)
        clean_text = clean_text.strip()
        return clean_text
    def normalize_seniority_level(level: str) -> str:
        """نرمال‌سازی سطح ارشدیت."""
        if not isinstance(level, str):
            return "نامشخص"
        level = level.lower()
        if "کارشناس ارشد" in level or "senior" in level:
            return "کارشناس ارشد"
        elif "کارشناس" in level or "specialist" in level:
            return "کارشناس"
        return level

    def clean_description(html_text):
        if not html_text:
            return ""
        soup = BeautifulSoup(html_text, "html.parser")
        cleaned_text = " ".join(soup.get_text().split())
        return cleaned_text
    def normalize_employment_type(emp) -> str:
        if not isinstance(emp, str):
            return "نامشخص"
        emp = emp.lower()
        if "تمام" in emp or "full" in emp:
            return "تمام‌وقت"
        elif "پاره" in emp or "part" in emp:
            return "پاره‌وقت"
        elif "دورکاری" in emp or "remote" in emp or "قراردادی" in emp or "پروژه" in emp:
            return "دورکاری/پروژه‌ای"
        return emp    
    job_data = data.get("data", {})
    job_data = data.get("data", {})
    skills = job_data.get("skills", [])
    skills_text = ",".join(skills) if skills else "" 
    job_details = {
        "title": job_data.get("title", ""),
        "description": clean_html(job_data.get("description", "")),
        "salary": job_data.get("salary", ""),
        "skills": skills_text,
        "seniorityLevel": normalize_seniority_level(job_data.get("seniorityLevel", "")),
        "city": job_data.get("locations", [{}])[0].get("city", {}).get("titleFa", ""),
        "resume": job_data.get("requiredWorkExperience", ""),
        "province": job_data.get("locations", [{}])[0].get("province", {}).get("titleFa", ""),
        "worktype": normalize_employment_type(job_data.get("workTypes", [{}])[0].get("titleFa", "")) if job_data.get("workTypes") and isinstance(job_data.get("workTypes"), list) else "",
        "location": {
            "province": job_data.get("locations", [{}])[0].get("province", {}).get("titleFa", ""),
            "city": job_data.get("locations", [{}])[0].get("city", {}).get("titleFa", ""),
            "region": job_data.get("district", "Iran")
        }
    }

    def add_ad(job_id ,job_title, job_salary, job_resume, job_description, skills_text, job_location, employment_type, job_degree):
        existing_ad = session.query(job_ads).filter_by(job_id=job_id).first()
        if existing_ad is None:
            new_ad = job_ads(
                job_id = job_id,
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
            
        session.add(new_ad)
        session.commit()
    try:
        add_ad(id,
                job_details["title"],
                job_details["salary"],
                job_details["resume"],
                job_details["description"],
                job_details["skills"],
                job_details["city"],
                job_details["worktype"],
                job_details["seniorityLevel"]
                )
    except :
        pass

    os.remove(file_path)
    time.sleep(2)          