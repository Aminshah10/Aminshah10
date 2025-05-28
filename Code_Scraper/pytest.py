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
        print(f"Page {page} - Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            with open(f"karbord_jobs{page}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"Json file number {page} created successfully.")
        else:
            try:
                error_details = response.json()
                print("Error Details:", json.dumps(error_details, indent=2))
            except:
                print("Could not parse error response as JSON")
                print("Raw Response:", response.text[:500])
            continue

    except Exception as e:
        print(f"Exception during request for page {page}: {e}")
        continue

    # Read and extract job IDs
    try:
        with open(f"karbord_jobs{page}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            job_posts = data["data"]["jobPosts"]
            
            for job in job_posts:
                job_id = job.get("id")
                job_ids.append(job_id)

    except Exception as e:
        print(f"Exception while reading karbord_jobs{page}.json: {e}")

    
    time.sleep(5)
    os.remove(f"karbord_jobs{page}.json")

for id in job_ids:
    print(id)
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
        print(f"Status Code: {response.status_code}")
         

        if response.status_code == 200:
            data = response.json()
            with open(f"karbord_job{id}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"JSON file number {str(id)} created successfully.")
        else:
            try:
                error_details = response.json()
                print("Error Details:", json.dumps(error_details, indent=2))
            except:
                print("Could not parse error response as JSON")
                # print("Raw Response:", response.text)

    except Exception as e:
        print(f"Exception: {e}")
    

    # Load the JSON file
    file_path = f"karbord_job{id}.json"  # Replace with your JSON file path
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}")
        exit(1)
    def clean_html(text: str) -> str:
        clean_text = re.sub(r'<[^>]+>', '', text or '')
        clean_text = re.sub(r'\n\s*\n', '\n', clean_text)
        clean_text = clean_text.strip()
        return clean_text
    # Clean HTML from description
    def clean_description(html_text):
        if not html_text:
            return ""
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_text, "html.parser")
        cleaned_text = " ".join(soup.get_text().split())
        return cleaned_text

    # Extract the required fields
    job_data = data.get("data", {})
    job_data = data.get("data", {})
    skills = job_data.get("skills", [])
    skills_text = ",".join(skills) if skills else "" 
    job_details = {
        "title": job_data.get("title", ""),
        "description": clean_html(job_data.get("description", "")),
        "salary": job_data.get("salary", ""),
        "skills": skills_text,
        "seniorityLevel": job_data.get("seniorityLevel", ""),
        "city": job_data.get("locations", [{}])[0].get("city", {}).get("titleFa", ""),
        "resume": job_data.get("requiredWorkExperience", ""),
        "province": job_data.get("locations", [{}])[0].get("province", {}).get("titleFa", ""),
        "worktype": job_data.get("workTypes", [{}])[0].get("titleFa", ""),
        "location": {
            "province": job_data.get("locations", [{}])[0].get("province", {}).get("titleFa", ""),
            "city": job_data.get("locations", [{}])[0].get("city", {}).get("titleFa", ""),
            "region": job_data.get("district", "Iran")
        }
    }

    def add_ad(job_title, job_salary, job_resume, job_description, skills_text, job_location, employment_type, degree):
        new_ad = job_ads(
            title=job_title,
            salary = job_salary,
            resume = job_resume,
            description = job_description,
            skills = skills_text,
            location = job_location,
            employment_type = employment_type,
            degree = degree)
            
        session.add(new_ad)
        session.commit()
    try:
        add_ad(job_details["title"],
                job_details["salary"],
                job_details["resume"],
                job_details["description"],
                job_details["skills"],
                job_details["city"],
                job_details["worktype"],
                job_details["seniorityLevel"]
                )
        print(f"Successfully added job ID {job_id} to database")
    except Exception as e:

        print(f"Error adding job ID {job_id} to database: {e}")

    # Clean up job-specific JSON file
    try:
        os.remove(file_path)
        
        print(f"Deleted {file_path}")
    except Exception as e:
        print(f"Error deleting {file_path}: {e}")

    time.sleep(2)  # Avoid rate limiting            