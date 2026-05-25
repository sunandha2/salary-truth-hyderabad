from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
from datetime import datetime

# --- CONFIG ---
SEARCH_QUERIES = [
    "data analyst Hyderabad",
    "business analyst Hyderabad",
    "data scientist Hyderabad",
    "analytics engineer Hyderabad",
    "BI analyst Hyderabad"
]
MAX_JOBS_PER_QUERY = 40  # 5 queries × 40 = 200 jobs

def random_sleep(min=2, max=5):
    """Mimic human behavior — don't get blocked"""
    time.sleep(random.uniform(min, max))

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver

def scrape_linkedin_jobs(query, driver, max_jobs=40):
    jobs = []
    
    # LinkedIn public job search — no login needed
    url = f"https://www.linkedin.com/jobs/search/?keywords={query.replace(' ', '%20')}&location=Hyderabad&f_TPR=r2592000"
    driver.get(url)
    random_sleep(3, 6)
    
    # Scroll to load more jobs
    for scroll in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        random_sleep(2, 4)
        try:
            # Click "See more jobs" if it appears
            see_more = driver.find_elements(By.XPATH, "//button[contains(text(),'See more jobs')]")
            if see_more:
                see_more[0].click()
                random_sleep(2, 3)
        except:
            pass
    
    # Find all job cards
    job_cards = driver.find_elements(By.CLASS_NAME, "base-card")
    print(f"  Found {len(job_cards)} job cards for: {query}")
    
    for card in job_cards[:max_jobs]:
        try:
            title = card.find_element(By.CLASS_NAME, "base-search-card__title").text.strip()
        except:
            title = "N/A"
        
        try:
            company = card.find_element(By.CLASS_NAME, "base-search-card__subtitle").text.strip()
        except:
            company = "N/A"
            
        try:
            location = card.find_element(By.CLASS_NAME, "job-search-card__location").text.strip()
        except:
            location = "N/A"
        
        try:
            salary = card.find_element(By.CLASS_NAME, "job-search-card__salary-info").text.strip()
        except:
            salary = "Not disclosed"  # This is the key data point!
        
        try:
            posted = card.find_element(By.CLASS_NAME, "job-search-card__listdate").text.strip()
        except:
            posted = "N/A"

        try:
            link = card.find_element(By.CLASS_NAME, "base-card__full-link").get_attribute("href")
        except:
            link = "N/A"

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "salary_raw": salary,
            "posted": posted,
            "search_query": query,
            "link": link,
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
    
    return jobs

def main():
    print(" Starting LinkedIn job scraper...")
    print("  Do NOT close the browser window that opens\n")
    
    driver = init_driver()
    all_jobs = []
    
    for query in SEARCH_QUERIES:
        print(f"Scraping: {query}")
        try:
            jobs = scrape_linkedin_jobs(query, driver, MAX_JOBS_PER_QUERY)
            all_jobs.extend(jobs)
            print(f"   Collected {len(jobs)} jobs")
            random_sleep(5, 10)  # Be polite between queries
        except Exception as e:
            print(f"  Error on {query}: {e}")
            continue
    
    driver.quit()
    
    # Save raw data
    df = pd.DataFrame(all_jobs)
    df = df.drop_duplicates(subset=['title', 'company'])
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"data/raw_jobs_{timestamp}.csv"
    df.to_csv(filename, index=False)
    
    print(f"\n Total jobs collected: {len(df)}")
    print(f" Salary disclosed: {(df['salary_raw'] != 'Not disclosed').sum()}")
    print(f" Salary hidden: {(df['salary_raw'] == 'Not disclosed').sum()}")
    print(f"Saved to: {filename}")
    
    return df

if __name__ == "__main__":
    df = main()
    print(df[['title', 'company', 'salary_raw']].head(10))