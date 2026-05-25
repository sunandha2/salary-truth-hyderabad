import os
import json
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import time

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_company_type(company_name):
    """Rule-based company classification"""
    mncs = ['amazon', 'google', 'apple', 'microsoft', 'meta', 'wipro', 
            'tcs', 'infosys', 'accenture', 'ibm', 'fedex', 'heineken',
            'lonza', 'apple', 'deloitte', 'pwc', 'kpmg', 'ey']
    
    company_lower = company_name.lower()
    for mnc in mncs:
        if mnc in company_lower:
            return 'MNC'
    return 'Startup/SME'

def extract_with_llm(title, company, description):
    """Use Groq to extract structured info from job listing"""
    
    # If no description, use title only
    text_to_analyze = description if description not in ['N/A', 'Could not fetch', ''] else f"Job title: {title} at {company}"
    
    prompt = f"""Analyze this job listing and return ONLY a JSON object. No explanation, no markdown, just raw JSON.

Job Title: {title}
Company: {company}
Content: {text_to_analyze[:1500]}

Return exactly this JSON structure:
{{
    "seniority": "Junior/Mid/Senior/Lead/Manager",
    "years_exp_min": <number or 0 if not mentioned>,
    "years_exp_max": <number or 0 if not mentioned>,
    "skills": [<list of up to 8 technical skills mentioned>],
    "management_role": <true or false>,
    "domain": "<primary domain: ecommerce/fintech/healthcare/logistics/general>",
    "education_required": "<MBA/BTech/Any/Not mentioned>",
    "num_skills": <count of skills listed>
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1
        )
        
        raw = response.choices[0].message.content.strip()
        
        # Clean JSON
        raw = raw.replace('```json', '').replace('```', '').strip()
        return json.loads(raw)
        
    except Exception as e:
        return {
            "seniority": "Unknown",
            "years_exp_min": 0,
            "years_exp_max": 0,
            "skills": [],
            "management_role": False,
            "domain": "general",
            "education_required": "Not mentioned",
            "num_skills": 0
        }

def main():
    # Load data
    try:
        df = pd.read_csv('data/jobs_with_descriptions.csv')
        print(f"Loaded jobs with descriptions: {len(df)}")
    except:
        df = pd.read_csv('data/clean_jobs.csv')
        df['description'] = 'N/A'
        print(f"Loaded clean jobs (no descriptions): {len(df)}")
    
    # Add company type classification
    df['company_type'] = df['company'].apply(classify_company_type)
    
    print(f"\nCompany breakdown:")
    print(df['company_type'].value_counts())
    
    # Extract with LLM
    print(f"\n Extracting skills with Groq LLM...")
    
    results = []
    for i, row in df.iterrows():
        print(f"  Processing {i+1}/{len(df)}: {row['title'][:40]}")
        
        extracted = extract_with_llm(
            row['title'],
            row['company'],
            row.get('description', 'N/A')
        )
        
        results.append({
            'title': row['title'],
            'company': row['company'],
            'company_type': row['company_type'],
            'salary_hidden': row['salary_raw'] == 'Not disclosed',
            'search_query': row['search_query'],
            **extracted
        })
        
        time.sleep(0.5)  # be gentle with API
    
    results_df = pd.DataFrame(results)
    
    # Explode skills into separate rows for analysis
    results_df['skills_str'] = results_df['skills'].apply(
        lambda x: ', '.join(x) if isinstance(x, list) else ''
    )
    
    results_df.to_csv('data/processed_jobs.csv', index=False)
    
    print(f"\n Processed {len(results_df)} jobs")
    print(f"\n KEY FINDING:")
    print(f"Salary hidden rate: {results_df['salary_hidden'].mean()*100:.1f}%")
    
    print(f"\nBy company type:")
    print(results_df.groupby('company_type')['salary_hidden'].mean() * 100)
    
    print(f"\nBy seniority:")
    print(results_df.groupby('seniority')['salary_hidden'].mean() * 100)
    
    print(f"\nAvg skills demanded by company type:")
    print(results_df.groupby('company_type')['num_skills'].mean())
    
    print(f"\nTop 15 most demanded skills:")
    all_skills = []
    for skills in results_df['skills']:
        if isinstance(skills, list):
            all_skills.extend(skills)
    
    skills_series = pd.Series(all_skills)
    print(skills_series.value_counts().head(15))
    
    return results_df

if __name__ == "__main__":
    df = main()