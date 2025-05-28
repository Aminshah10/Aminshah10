import re
import json
import unicodedata
from typing import List, Dict
def load_json_data(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    job_posts = data.get('data', {}).get('jobPosts', [])
    extracted_jobs = []
    for job in job_posts:
        job_data = {
            'title': job.get('title', ''),
            'location': (
                f"{job.get('location', {}).get('province', {}).get('titleFa', 'نامشخص')} - "
                f"{job.get('location', {}).get('city', {}).get('titleFa', 'نامشخص')} - "
                f"{job.get('location', {}).get('region', {}).get('titleFa', 'نامشخص')}"
            ).strip(),
            'province': job.get('location', {}).get('province', {}).get('titleFa', 'نامشخص'),
            'city': job.get('location', {}).get('city', {}).get('titleFa', 'نامشخص'),
            'region': job.get('location', {}).get('region', {}).get('titleFa', 'نامشخص'),
            'workType': job.get('workType', {}).get('titleFa', 'نامشخص'),
            'seniorityLevel': job.get('seniorityLevel', {}).get('titleFa', 'نامشخص'),
            'salary': job.get('salary', {}).get('titleFa', 'نامشخص')
        }
        extracted_jobs.append(job_data)
    return extracted_jobs
class JobCleaner:
    def __init__(self, job_ads: List[Dict]):
        self.job_ads = job_ads
    def is_valid_ad(self, ad: Dict) -> bool:
        return bool(ad.get('title') and (ad.get('province') != 'نامشخص' or ad.get('city') != 'نامشخص'))
    def not_valid_ad(self, ad: Dict) -> None:
        print(f"آگهی نامعتبر: {ad.get('title', 'بدون عنوان')}")
    def clean_all(self) -> List[Dict]:
        cleaned = []
        for ad in self.job_ads:
            if self.is_valid_ad(ad):
                cleaned_ad = self.clean_entry(ad)
                cleaned.append(cleaned_ad)
            else:
                self.not_valid_ad(ad)
        return cleaned
    def clean_entry(self, ad: Dict) -> Dict:
        ad = self.normalize_text_fields(ad)
        ad['salary'] = self.normalize_salary(ad.get('salary', 'نامشخص'))
        ad['location'] = self.normalize_location(ad.get('location', 'نامشخص'))
        ad['province'] = self.normalize_location(ad.get('province', 'نامشخص'))
        ad['city'] = self.normalize_location(ad.get('city', 'نامشخص'))
        ad['region'] = self.normalize_location(ad.get('region', 'نامشخص'))
        ad['workType'] = self.normalize_employment_type(ad.get('workType', 'نامشخص'))
        ad['seniorityLevel'] = self.normalize_seniority_level(ad.get('seniorityLevel', 'نامشخص'))
        return ad
    def normalize_text_fields(self, ad: Dict) -> Dict:
        if not isinstance(ad, dict):
            return {}
        cleaned = {}
        for key, value in ad.items():
            if isinstance(value, str):
                text = unicodedata.normalize("NFKC", value)
                text = text.strip().replace('\u200c', ' ')
                text = re.sub(r"\s+", " ", text)
                cleaned[key] = text
            else:
                cleaned[key] = value
        return cleaned
    def normalize_salary(self, salary_str: str) -> int:
        if not isinstance(salary_str, str) or salary_str == 'نامشخص':
            return 0
        numbers = re.findall(r'\d+', salary_str)
        if len(numbers) == 2:
            min_salary, max_salary = map(int, numbers)
            return (min_salary + max_salary) // 2 * 1000000
        elif len(numbers) == 1:
            return int(numbers[0]) * 1000000
        return 0
    def normalize_location(self, location: str) -> str:
        city_map = {
            "آذربایجان شرقی": "آذربایجان شرقی",
            "آذربایجان غربی": "آذربایجان غربی",
            "اردبیل": "اردبیل",
            "اصفهان": "اصفهان",
            "isfahan": "اصفهان",
            "البرز": "البرز",
            "alborz": "البرز",
            "ایلام": "ایلام",
            "بوشهر": "بوشهر",
            "تهران": "تهران",
            "tehran": "تهران",
            "چهارمحال و بختیاری": "چهارمحال و بختیاری",
            "خراسان جنوبی": "خراسان جنوبی",
            "خراسان رضوی": "خراسان رضوی",
            "خراسان شمالی": "خراسان شمالی",
            "خوزستان": "خوزستان",
            "khuzestan": "خوزستان",
            "زنجان": "زنجان",
            "سمنان": "سمنان",
            "سیستان و بلوچستان": "سیستان و بلوچستان",
            "فارس": "فارس",
            "fars": "فارس",
            "ق bribesوین": "قزوین",
            "قم": "قم",
            "qom": "قم",
            "کردستان": "کردستان",
            "کرمان": "کرمان",
            "kerman": "کرمان",
            "کرمانشاه": "کرمانشاه",
            "kermanshah": "کرمانشاه",
            "کهگیلویه و بویراحمد": "کهگیلویه و بویراحمد",
            "گلستان": "گلستان",
            "گیلان": "گیلان",
            "gilan": "گیلان",
            "لرستان": "لرستان",
            "مازندران": "مازندران",
            "mazandaran": "مازندران",
            "مرکزی": "مرکزی",
            "هرمزگان": "هرمزگان",
            "همدان": "همدان",
            "یزد": "یزد",
            "yazd": "یزد"
        }
        if not isinstance(location, str) or not location or location == 'نامشخص':
            return "نامشخص"
        cleaned_location = location.strip()
        if cleaned_location in city_map:
            return city_map[cleaned_location]
        cleaned_location_lower = cleaned_location.lower()
        for key, value in city_map.items():
            if key.lower() in cleaned_location_lower:
                return value
        return cleaned_location 
    def normalize_employment_type(self, emp: str) -> str:
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
    def normalize_seniority_level(self, level: str) -> str:
        if not isinstance(level, str):
            return "نامشخص"
        level = level.lower()
        if "کارشناس ارشد" in level or "senior" in level:
            return "کارشناس ارشد"
        elif "کارشناس" in level or "specialist" in level:
            return "کارشناس"
        return level 
    def sort_jobs(self, key: str = 'salary', reverse: bool = True) -> List[Dict]:
        cleaned_jobs = self.clean_all()
        return sorted(cleaned_jobs, key=lambda x: x.get(key, 0), reverse=reverse)
if __name__ == "__main__":
    job_ads = load_json_data('jobvision_jobs.json')
    cleaner = JobCleaner(job_ads)
    sorted_jobs = cleaner.sort_jobs(key='salary', reverse=True)
    for job in sorted_jobs:
        print(job)