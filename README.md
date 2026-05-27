# Salary Truth: Hyderabad 

> I scraped 115 data analyst job listings from LinkedIn 
> in Hyderabad. Salary disclosed by 0 out of 115 companies.

## The Finding
Not a single company — including Amazon, Google, Apple, 
and Wipro — disclosed salary in their Hyderabad job listings.
This project investigates what they're hiding and why.

## Live App
🔗 https://salary-truth-hyderabad-u7xaqwxhs2pyiuc5hmeje2.streamlit.app/

## Research Questions
- Do MNCs hide salary more than Indian startups?
- Do senior roles hide compensation more than junior ones?
- Which skills are demanded most by companies hiding pay?
- Is there a pattern in who hides vs who discloses?

## What I Built
-  LinkedIn scraper (Selenium) across 5 search queries
-  LLM extraction of skills, seniority, experience from JDs
-  Analysis of salary transparency patterns by company type
-  Published findings on Medium

## Tech Stack
Python · Selenium · Pandas · Groq API (Llama 3.3) · Plotly · Streamlit

## Data
- 115 job listings scraped May 2026
- Companies: Amazon, Google, Apple, Wipro, FedEx + 60 more
- Roles: Data Analyst, Business Analyst, Data Scientist, BI Analyst

## Progress
- [x] Day 1 — Project setup + environment
- [x] Day 2 — Scraper built, 115 jobs collected, 0% disclosure found
- [x] Day 3 — Groq LLM extracted skills + seniority — 100% hidden rate confirmed across all company types and seniority levels
- [x] Day 4 — 5 visualizations built (headline, company type, seniority, skills, skills vs transparency)
- [x] Day 5 — Live deployment URL added
- [x] Day 6 — Streamlit app + Medium article published

## Findings So Far
**100% salary hidden rate — no exceptions.**
- MNCs (Amazon, Google, Apple, Wipro) → 100% hidden
- Startups → 100% hidden
- Junior roles → 100% hidden
- Senior/Manager roles → 100% hidden

Top skills demanded while hiding pay: AI, ML, Power BI, Python, Snowflake

## Visualizations Built
| Chart | Finding |
|---|---|
| Salary Disclosure Rate | 0% disclosed, 100% hidden |
| MNC vs Startup | Both hide 100% — no difference |
| By Seniority | Junior to Manager — all hide 100% |
| Top Skills Demanded | AI, ML, Power BI, Python, Snowflake |
| Skills vs Transparency | More skills demanded = still 100% hidden |

## Author
Built as an original research project — dataset created 
from scratch, no Kaggle involved.