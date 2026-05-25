import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

os.makedirs('visuals', exist_ok=True)

df = pd.read_csv('data/processed_jobs.csv')

# Fix skills column
import ast
def parse_skills(s):
    try:
        if isinstance(s, str) and s.startswith('['):
            return ast.literal_eval(s)
        return []
    except:
        return []

df['skills_list'] = df['skills'].apply(parse_skills)
df['num_skills'] = df['skills_list'].apply(len)

print(f"✅ Loaded {len(df)} jobs")
print(f"Salary hidden: {df['salary_hidden'].sum()}/{len(df)}")

# ── CHART 1: The headline finding ──────────────────────────────
fig1 = go.Figure()

fig1.add_trace(go.Bar(
    x=['Salary Disclosed', 'Salary Hidden'],
    y=[0, 115],
    marker_color=['#2ecc71', '#e74c3c'],
    text=['0 (0%)', '115 (100%)'],
    textposition='outside',
    textfont=dict(size=18, color='white'),
))

fig1.update_layout(
    title=dict(
        text='Salary Transparency in Hyderabad Data Jobs<br><sup>115 LinkedIn listings scraped May 2026</sup>',
        font=dict(size=20),
        x=0.5
    ),
    plot_bgcolor='#1a1a2e',
    paper_bgcolor='#1a1a2e',
    font=dict(color='white'),
    yaxis=dict(title='Number of Jobs', range=[0, 130]),
    xaxis=dict(title=''),
    showlegend=False,
    height=500,
)

fig1.write_html('visuals/chart1_headline.html')
fig1.write_image('visuals/chart1_headline.png', width=800, height=500, scale=2)
print("✅ Chart 1 saved — headline finding")

# ── CHART 2: By company type ───────────────────────────────────
company_counts = df.groupby('company_type').agg(
    total=('salary_hidden', 'count'),
    hidden=('salary_hidden', 'sum')
).reset_index()
company_counts['disclosed'] = company_counts['total'] - company_counts['hidden']

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    name='Salary Hidden',
    x=company_counts['company_type'],
    y=company_counts['hidden'],
    marker_color='#e74c3c',
    text=company_counts['hidden'],
    textposition='auto',
))
fig2.add_trace(go.Bar(
    name='Salary Disclosed',
    x=company_counts['company_type'],
    y=company_counts['disclosed'],
    marker_color='#2ecc71',
    text=company_counts['disclosed'],
    textposition='auto',
))

fig2.update_layout(
    title=dict(
        text='Salary Hidden: MNC vs Startup<br><sup>Both hide 100% — no exceptions</sup>',
        font=dict(size=20),
        x=0.5
    ),
    barmode='stack',
    plot_bgcolor='#1a1a2e',
    paper_bgcolor='#1a1a2e',
    font=dict(color='white'),
    height=500,
)

fig2.write_html('visuals/chart2_company_type.html')
fig2.write_image('visuals/chart2_company_type.png', width=800, height=500, scale=2)
print("✅ Chart 2 saved — company type")

# ── CHART 3: By seniority ──────────────────────────────────────
seniority_order = ['Junior', 'Mid', 'Senior', 'Lead', 'Manager']
seniority_counts = df[df['seniority'].isin(seniority_order)].groupby('seniority').agg(
    total=('salary_hidden', 'count'),
    hidden=('salary_hidden', 'sum')
).reset_index()
seniority_counts['hidden_pct'] = seniority_counts['hidden'] / seniority_counts['total'] * 100

fig3 = px.bar(
    seniority_counts,
    x='seniority',
    y='hidden_pct',
    color='hidden_pct',
    color_continuous_scale=['#f39c12', '#e74c3c'],
    text=seniority_counts['hidden_pct'].apply(lambda x: f'{x:.0f}%'),
    title='Salary Hidden Rate by Seniority Level<br><sup>Does hiding increase with seniority?</sup>',
)

fig3.update_traces(textposition='outside')
fig3.update_layout(
    plot_bgcolor='#1a1a2e',
    paper_bgcolor='#1a1a2e',
    font=dict(color='white'),
    yaxis=dict(title='% Jobs Hiding Salary', range=[0, 120]),
    xaxis=dict(title='Seniority Level'),
    coloraxis_showscale=False,
    height=500,
    title_x=0.5
)

fig3.write_html('visuals/chart3_seniority.html')
fig3.write_image('visuals/chart3_seniority.png', width=800, height=500, scale=2)
print("✅ Chart 3 saved — seniority")

# ── CHART 4: Top skills demanded ──────────────────────────────
all_skills = []
for skills in df['skills_list']:
    all_skills.extend(skills)

skills_df = pd.Series(all_skills).value_counts().head(12).reset_index()
skills_df.columns = ['skill', 'count']

fig4 = px.bar(
    skills_df,
    x='count',
    y='skill',
    orientation='h',
    color='count',
    color_continuous_scale=['#3498db', '#9b59b6'],
    text='count',
    title='Top Skills Demanded — While Hiding Salary<br><sup>What they want but won\'t pay transparently for</sup>',
)

fig4.update_traces(textposition='outside')
fig4.update_layout(
    plot_bgcolor='#1a1a2e',
    paper_bgcolor='#1a1a2e',
    font=dict(color='white'),
    yaxis=dict(title='', autorange='reversed'),
    xaxis=dict(title='Number of Job Listings'),
    coloraxis_showscale=False,
    height=550,
    title_x=0.5
)

fig4.write_html('visuals/chart4_skills.html')
fig4.write_image('visuals/chart4_skills.png', width=800, height=550, scale=2)
print("✅ Chart 4 saved — top skills")

# ── CHART 5: Skills demanded vs salary transparency ───────────
df['skill_bucket'] = pd.cut(
    df['num_skills'],
    bins=[-1, 0, 2, 4, 10],
    labels=['0 skills', '1-2 skills', '3-4 skills', '5+ skills']
)

skill_transparency = df.groupby('skill_bucket', observed=True).agg(
    total=('salary_hidden', 'count'),
    hidden=('salary_hidden', 'sum')
).reset_index()
skill_transparency['hidden_pct'] = skill_transparency['hidden'] / skill_transparency['total'] * 100

fig5 = px.bar(
    skill_transparency,
    x='skill_bucket',
    y='hidden_pct',
    color='hidden_pct',
    color_continuous_scale=['#f39c12', '#e74c3c'],
    text=skill_transparency['hidden_pct'].apply(lambda x: f'{x:.0f}%'),
    title='More Skills Demanded = More Salary Hidden?<br><sup>Analyzing if skill demands correlate with opacity</sup>',
)

fig5.update_traces(textposition='outside')
fig5.update_layout(
    plot_bgcolor='#1a1a2e',
    paper_bgcolor='#1a1a2e',
    font=dict(color='white'),
    yaxis=dict(title='% Jobs Hiding Salary', range=[0, 120]),
    xaxis=dict(title='Skills Demanded in Job Listing'),
    coloraxis_showscale=False,
    height=500,
    title_x=0.5
)

fig5.write_html('visuals/chart5_skills_vs_transparency.html')
fig5.write_image('visuals/chart5_skills_vs_transparency.png', width=800, height=500, scale=2)
print("✅ Chart 5 saved — skills vs transparency")

print("\n All 5 charts saved to visuals/")
print("\nFiles created:")
for f in os.listdir('visuals'):
    print(f"  {f}")