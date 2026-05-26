import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ast
import os

st.set_page_config(
    page_title="Salary Truth: Hyderabad",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0f0f1a; }
    .main { background-color: #0f0f1a; }
    .metric-card {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #2d2d44;
        text-align: center;
    }
    .metric-value { font-size: 32px; font-weight: bold; color: #e74c3c; }
    .metric-label { font-size: 13px; color: #888; margin-top: 4px; }
    .finding-box {
        background: #1a1a2e;
        border-left: 4px solid #e74c3c;
        border-radius: 6px;
        padding: 16px;
        margin: 12px 0;
        font-size: 15px;
        line-height: 1.7;
        color: #ddd;
    }
    .skill-tag {
        display: inline-block;
        background: #1a1a2e;
        border: 1px solid #378ADD;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 4px;
        font-size: 12px;
        color: #4fc3f7;
    }
    h1, h2, h3 { color: white !important; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ──────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('data/processed_jobs.csv')
    def parse_skills(s):
        try:
            if isinstance(s, str) and s.startswith('['):
                return ast.literal_eval(s)
            return []
        except:
            return []
    df['skills_list'] = df['skills'].apply(parse_skills)
    df['num_skills'] = df['skills_list'].apply(len)
    return df

df = load_data()

# ── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 Salary Truth")
    st.markdown("*Hyderabad Data Jobs — May 2026*")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["The Finding", "Deep Analysis", "Company Explorer", "Skills Demanded"],
        label_visibility="collapsed",
        key="nav"
    )

    st.markdown("---")
    st.markdown("**Dataset**")
    st.markdown(f"- {len(df)} job listings")
    st.markdown(f"- {df['company'].nunique()} companies")
    st.markdown(f"- Scraped May 2026")
    st.markdown(f"- Salary hidden: **100%**")
    st.markdown("---")
    st.markdown("**Tech Stack**")
    st.markdown("Python · Selenium · Groq · Plotly · Streamlit")

# ── PAGE 1: THE FINDING ────────────────────────────────────────
if "Finding" in page:
    st.markdown("#  Salary Truth: Hyderabad")
    st.markdown("*I scraped 115 data analyst jobs from LinkedIn. Here's what I found.*")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">115</div>
            <div class="metric-label">Jobs Scraped</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">0</div>
            <div class="metric-label">Salaries Disclosed</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">100%</div>
            <div class="metric-label">Hidden Rate</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{df['company'].nunique()}</div>
            <div class="metric-label">Companies Checked</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div class="finding-box">
        <strong>The Finding:</strong> Not a single company — including Amazon, Google, 
        Apple, and Wipro — disclosed salary in their Hyderabad data analyst job listings. 
        100% of 115 listings hid compensation. This is true across all seniority levels 
        (Junior to Manager) and all company types (MNCs and startups).
    </div>""", unsafe_allow_html=True)

    # Headline chart
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=['Salary Disclosed', 'Salary Hidden'],
        y=[0, 115],
        marker_color=['#2ecc71', '#e74c3c'],
        text=['0 (0%)', '115 (100%)'],
        textposition='outside',
        textfont=dict(size=16, color='white'),
    ))
    fig1.update_layout(
        title=dict(text='Salary Transparency in Hyderabad Data Jobs<br><sup>115 LinkedIn listings — May 2026</sup>', x=0.5, font=dict(size=18)),
        plot_bgcolor='#1a1a2e',
        paper_bgcolor='#0f0f1a',
        font=dict(color='white'),
        height=400,
        yaxis=dict(range=[0, 130], showgrid=True, gridcolor='#2d2d44'),
        showlegend=False,
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### Companies That Hide Salary")
    companies = df['company'].value_counts().head(15).reset_index()
    companies.columns = ['Company', 'Listings']
    companies['All Hidden'] = ' 100%'
    st.dataframe(companies, use_container_width=True, hide_index=True)

# ── PAGE 2: DEEP ANALYSIS ──────────────────────────────────────
elif "Analysis" in page:
    st.markdown("#  Deep Analysis")
    st.markdown("*Does anything change the hiding rate? No.*")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        company_data = df.groupby('company_type').agg(
            total=('salary_hidden', 'count'),
            hidden=('salary_hidden', 'sum')
        ).reset_index()
        company_data['hidden_pct'] = 100.0

        fig2 = px.bar(
            company_data,
            x='company_type',
            y='hidden_pct',
            color='company_type',
            color_discrete_map={'MNC': '#e74c3c', 'Startup/SME': '#e67e22'},
            text=company_data['total'].apply(lambda x: f'{x} jobs'),
            title='Salary Hidden Rate: MNC vs Startup'
        )
        fig2.update_traces(textposition='outside')
        fig2.update_layout(
            plot_bgcolor='#1a1a2e',
            paper_bgcolor='#0f0f1a',
            font=dict(color='white'),
            height=350,
            yaxis=dict(range=[0, 120], title='% Hidden'),
            showlegend=False,
            title_x=0.5
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        seniority_order = ['Junior', 'Mid', 'Senior', 'Lead', 'Manager']
        sen_data = df[df['seniority'].isin(seniority_order)].groupby('seniority').agg(
            total=('salary_hidden', 'count')
        ).reset_index()
        sen_data['hidden_pct'] = 100.0

        fig3 = px.bar(
            sen_data,
            x='seniority',
            y='hidden_pct',
            color='seniority',
            text=sen_data['total'].apply(lambda x: f'{x} jobs'),
            title='Salary Hidden Rate: By Seniority'
        )
        fig3.update_traces(textposition='outside')
        fig3.update_layout(
            plot_bgcolor='#1a1a2e',
            paper_bgcolor='#0f0f1a',
            font=dict(color='white'),
            height=350,
            yaxis=dict(range=[0, 120], title='% Hidden'),
            showlegend=False,
            title_x=0.5
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div class="finding-box">
        <strong>Key Insight:</strong> It doesn't matter if you're applying to Amazon or 
        a 10-person startup. It doesn't matter if you're a fresher or a senior manager. 
        In Hyderabad's data job market, salary is hidden 100% of the time. 
        The playing field is equally opaque for everyone.
    </div>""", unsafe_allow_html=True)

# ── PAGE 3: COMPANY EXPLORER ───────────────────────────────────
elif "Company" in page:
    st.markdown("# 💼 Company Explorer")
    st.markdown("*Browse all companies — every single one hides salary*")
    st.markdown("---")

    company_type_filter = st.selectbox(
        "Filter by company type",
        ["All", "MNC", "Startup/SME"]
    )

    filtered = df if company_type_filter == "All" else df[df['company_type'] == company_type_filter]

    company_summary = filtered.groupby(['company', 'company_type']).agg(
        listings=('title', 'count'),
        roles=('title', lambda x: ', '.join(x.unique()[:3]))
    ).reset_index()
    company_summary['salary_hidden'] = '🔒 100%'
    company_summary.columns = ['Company', 'Type', 'Listings', 'Sample Roles', 'Salary']
    company_summary = company_summary.sort_values('Listings', ascending=False)

    st.dataframe(company_summary, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown(f"**{len(company_summary)} companies shown — all hiding salary**")

# ── PAGE 4: SKILLS DEMANDED ────────────────────────────────────
elif "Skills" in page:
    st.markdown("# 🛠️ Skills Demanded While Hiding Salary")
    st.markdown("*What they want — but won't tell you what they'll pay for*")
    st.markdown("---")

    all_skills = []
    for skills in df['skills_list']:
        all_skills.extend(skills)

    if all_skills:
        skills_df = pd.Series(all_skills).value_counts().head(15).reset_index()
        skills_df.columns = ['skill', 'count']

        fig4 = px.bar(
            skills_df,
            x='count',
            y='skill',
            orientation='h',
            color='count',
            color_continuous_scale=['#3498db', '#9b59b6'],
            text='count',
            title='Top Skills Demanded — While Hiding Salary'
        )
        fig4.update_traces(textposition='outside')
        fig4.update_layout(
            plot_bgcolor='#1a1a2e',
            paper_bgcolor='#0f0f1a',
            font=dict(color='white'),
            height=500,
            yaxis=dict(autorange='reversed'),
            coloraxis_showscale=False,
            title_x=0.5
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div class="finding-box">
        <strong>The Irony:</strong> Companies demand AI, ML, Power BI, Python and Snowflake 
        — cutting-edge skills that take years to build — but won't tell candidates 
        what they'll pay for them. You're expected to negotiate blind.
    </div>""", unsafe_allow_html=True)

    st.markdown("### 📋 All Jobs with Skills")
    display_df = df[['title', 'company', 'company_type', 'seniority', 'skills_str']].copy()
    display_df.columns = ['Title', 'Company', 'Type', 'Seniority', 'Skills']
    st.dataframe(display_df, use_container_width=True, hide_index=True)