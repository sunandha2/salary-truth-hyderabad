from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random

print("📄 Fetching job descriptions...")

df = pd.read_csv('data/clean_jobs.csv')
print(f"Jobs to fetch: {len(df)}")

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

descriptions = []

for i, row in df.iterrows():
    if pd.isna(row['link']) or row['link'] == 'N/A':
        descriptions.append('N/A')
        continue
    
    try:
        driver.get(row['link'])
        time.sleep(random.uniform(3, 5))
        
        # Try to get description
        try:
            desc = driver.find_element(
                By.CLASS_NAME, 
                "description__text"
            ).text.strip()
        except:
            try:
                desc = driver.find_element(
                    By.CLASS_NAME,
                    "show-more-less-html__markup"
                ).text.strip()
            except:
                desc = "Could not fetch"
        
        descriptions.append(desc[:2000])  # cap at 2000 chars
        print(f"  ✅ {i+1}/{len(df)}: {row['title'][:40]}")
        
    except Exception as e:
        descriptions.append("Could not fetch")
        print(f"  ❌ {i+1}/{len(df)}: {e}")
    
    time.sleep(random.uniform(2, 4))

driver.quit()

df['description'] = descriptions
df.to_csv('data/jobs_with_descriptions.csv', index=False)

fetched = len([d for d in descriptions if d not in ['N/A', 'Could not fetch']])
print(f"\n✅ Descriptions fetched: {fetched}/{len(df)}")
print(f"✅ Saved to data/jobs_with_descriptions.csv")