from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up Chrome options to avoid detection
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")

# Set up the Chrome driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
job_cleaned = []
try:
    for i in range(1,3):
        # Navigate to the website
        page_link = f"https://jobvision.ir/jobs/category/developer?page={i}&sort=1"
        driver.get(page_link)

        # Wait until job cards are loaded
        print("Waiting for job cards to load...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "job-card"))
        )
        print("Job cards found.")

        # Find all <a> tags with href inside job-card elements
        job_links = driver.find_elements(By.CSS_SELECTOR, "job-card a[href]")
        print(f"Found {len(job_links)} <a> tags with href.")
        
        # gettin href from each link
        for i, link in enumerate(job_links, 1):
            href_value = link.get_attribute("href")
            if "companies" in href_value or "category" in href_value:
                pass
            else:
                job_cleaned.append(href_value)
        # sleep between each page for 5 seconds
        time.sleep(5)


finally:
    # Close the browser
    print(len(job_cleaned))
    print("Closing browser...")
    driver.quit()

