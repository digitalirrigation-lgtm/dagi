import streamlit as st
import requests
import json
import base64
from datetime import datetime, timedelta
import time
import pandas as pd
from calendar import monthcalendar
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ========== SET ETHIOPIA TIME ZONE ==========
os.environ['TZ'] = 'Africa/Addis_Ababa'
try:
    time.tzset()
except:
    pass

# ========== GET TOKEN FROM STREAMLIT SECRETS ==========

try:
    TOKEN = st.secrets["TOKEN"]
except:
    TOKEN = None

USER = "digitalirrigation-lgtm"
REPO = "dagi"
FILE = "data.json"

if not TOKEN:
    st.error("❌ No token found! Add TOKEN to Streamlit secrets.")
    st.stop()

st.set_page_config(
    page_title="📚 Dagi Superhero CV System", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== ETHIOPIA TIME ==========
def get_ethiopia_time():
    try:
        import pytz
        ethiopia_tz = pytz.timezone('Africa/Addis_Ababa')
        return datetime.now(ethiopia_tz)
    except:
        return datetime.utcnow() + timedelta(hours=3)

# ========== CUSTOM CSS ==========

st.markdown("""
<style>
    .welcome-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        margin: 10px 0 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 1px solid #e94560;
    }
    .welcome-title { font-size: 2.2em; font-weight: bold; color: #e94560; }
    .welcome-time { font-size: 2em; opacity: 0.9; font-weight: bold; }
    .welcome-date { font-size: 1.2em; opacity: 0.8; }
    .welcome-location { font-size: 1em; opacity: 0.7; }
    
    .cv-master {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 5px solid #e94560;
    }
    .cv-minor {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 5px solid #00d2ff;
    }
    .cv-section {
        background: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .cv-section-title { color: #e94560; font-weight: bold; font-size: 1.2em; }
    .cv-minor-title { color: #00d2ff; font-weight: bold; font-size: 1.2em; }
    
    .ss-sort { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 15px; margin: 5px 0; text-align: center; }
    .ss-set { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 15px; border-radius: 15px; margin: 5px 0; text-align: center; }
    .ss-shine { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 15px; border-radius: 15px; margin: 5px 0; text-align: center; }
    .ss-standardize { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 15px; border-radius: 15px; margin: 5px 0; text-align: center; }
    .ss-sustain { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 15px; border-radius: 15px; margin: 5px 0; text-align: center; }
    
    .deadline-red { background: #dc3545; color: white; padding: 5px 15px; border-radius: 25px; font-weight: bold; display: inline-block; animation: blink 1s infinite; }
    .deadline-yellow { background: #ffc107; color: black; padding: 5px 15px; border-radius: 25px; font-weight: bold; display: inline-block; }
    .deadline-green { background: #28a745; color: white; padding: 5px 15px; border-radius: 25px; font-weight: bold; display: inline-block; }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .history-item { 
        padding: 12px; 
        background: #f8f9fa; 
        border-radius: 10px; 
        margin: 5px 0;
        border-left: 5px solid #007bff;
        transition: all 0.3s;
        cursor: pointer;
    }
    .history-item:hover { background: #e9ecef; transform: translateX(5px); }
    
    .word-export {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border: 3px solid #007bff;
        white-space: pre-wrap;
        font-family: 'Arial', sans-serif;
        min-height: 150px;
        max-height: 500px;
        overflow-y: auto;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .note-card {
        background: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 10px 0;
    }
    
    .stats-card {
        background: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border: 2px solid #e9ecef;
    }
    .stats-number { font-size: 2em; font-weight: bold; color: #007bff; }
    .stats-label { color: #6c757d; font-size: 0.9em; }
    
    .calendar-day {
        padding: 10px;
        margin: 2px;
        border-radius: 10px;
        text-align: center;
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        transition: all 0.3s;
        cursor: pointer;
    }
    .calendar-day:hover { background: #007bff; color: white; transform: scale(1.05); }
    .calendar-day.selected { background: #007bff; color: white; border-color: #007bff; }
    .calendar-day.has-items { background: #28a745; color: white; }
    .calendar-day.today { border: 3px solid #007bff; font-weight: bold; }
    
    .opportunity-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #e94560;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .small-btn {
        padding: 4px 12px;
        font-size: 0.8em;
        border-radius: 5px;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ========== WELCOME SECTION WITH ETHIOPIA TIME ==========

ethiopia_time = get_ethiopia_time()
day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_name = day_names[ethiopia_time.weekday()]

st.markdown(f"""
<div class="welcome-box">
    <div class="welcome-title">🦸 Welcome, Superhero Dagim!</div>
    <div class="welcome-time">🕐 {ethiopia_time.strftime('%I:%M:%S %p')}</div>
    <div class="welcome-date">📅 {ethiopia_time.strftime('%B %d, %Y')} - {day_name}</div>
    <div class="welcome-location">📍 Addis Ababa, Ethiopia (UTC+3)</div>
</div>
""", unsafe_allow_html=True)

# ========== GITHUB FUNCTIONS ==========

def get_data():
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
    headers = {'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()['content']
            decoded = base64.b64decode(content).decode('utf-8')
            data = json.loads(decoded)
            
            if 'scholarships' not in data: data['scholarships'] = []
            if 'jobs' not in data: data['jobs'] = []
            if 'masterCV' not in data: 
                data['masterCV'] = {"title": "ZEDAGIM TESFAYE TANTU - Master CV", "content": "", "lastUpdated": "", "sections": []}
            if 'minorCV' not in data:
                data['minorCV'] = {"title": "ZEDAGIM TESFAYE TANTU - Minor CV", "content": "", "lastUpdated": "", "sections": []}
            if 'history' not in data: data['history'] = []
            if 'notes' not in data: data['notes'] = []
            return data
        else:
            default_data = {
                "scholarships": [], "jobs": [], 
                "masterCV": {"title": "ZEDAGIM TESFAYE TANTU - Master CV", "content": "", "lastUpdated": "", "sections": []},
                "minorCV": {"title": "ZEDAGIM TESFAYE TANTU - Minor CV", "content": "", "lastUpdated": "", "sections": []},
                "history": [], "notes": []
            }
            save_data(default_data)
            return default_data
    except:
        return {
            "scholarships": [], "jobs": [], 
            "masterCV": {"title": "ZEDAGIM TESFAYE TANTU - Master CV", "content": "", "lastUpdated": "", "sections": []},
            "minorCV": {"title": "ZEDAGIM TESFAYE TANTU - Minor CV", "content": "", "lastUpdated": "", "sections": []},
            "history": [], "notes": []
        }

def save_data(data):
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
    headers = {'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3+json'}
    
    try:
        sha = None
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                sha = response.json()['sha']
        except:
            pass
        
        content = base64.b64encode(json.dumps(data, indent=2, default=str).encode('utf-8')).decode('utf-8')
        payload = {'message': f'Update - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 'content': content, 'branch': 'main'}
        if sha: payload['sha'] = sha
        
        response = requests.put(url, headers=headers, json=payload, timeout=10)
        return response.status_code in [200, 201]
    except:
        return False

def add_history(data, action, item_type, item_name, details=""):
    if 'history' not in data: data['history'] = []
    eth_time = get_ethiopia_time()
    data['history'].append({
        "timestamp": eth_time.strftime("%Y-%m-%d %H:%M:%S"),
        "date": eth_time.strftime("%Y-%m-%d"),
        "action": action,
        "type": item_type,
        "name": item_name,
        "details": details
    })
    return data

def generate_individual_word(item, item_type):
    word = "=" * 70 + "\n"
    word += f"📚 {item_type.upper()} DETAILS\n"
    word += "=" * 70 + "\n\n"
    
    if item_type == "scholarship":
        word += f"🎓 Name: {item.get('name', 'N/A')}\n"
        word += f"🏛️ University: {item.get('uni', 'N/A')}\n"
        word += f"📅 Deadline: {item.get('deadline', 'N/A')}\n"
        word += f"🌍 Country: {item.get('country', 'N/A')}\n"
        word += f"📊 Status: {item.get('status', 'active')}\n"
        word += f"📝 Notes: {item.get('notes', 'N/A')}\n"
        word += f"🔗 Link: {item.get('link', 'N/A')}\n"
        word += f"🕐 Added: {item.get('createdAt', 'N/A')}\n"
    else:
        word += f"💼 Title: {item.get('title', 'N/A')}\n"
        word += f"🏢 Company: {item.get('company', 'N/A')}\n"
        word += f"📅 Deadline: {item.get('deadline', 'N/A')}\n"
        word += f"📍 Location: {item.get('location', 'N/A')}\n"
        word += f"📊 Status: {item.get('status', 'active')}\n"
        word += f"📝 Notes: {item.get('notes', 'N/A')}\n"
        word += f"🔗 Link: {item.get('link', 'N/A')}\n"
        word += f"🕐 Added: {item.get('createdAt', 'N/A')}\n"
    
    eth_time = get_ethiopia_time()
    word += "\n" + "=" * 70 + "\n"
    word += f"📅 Generated: {eth_time.strftime('%Y-%m-%d %H:%M:%S')} (Addis Ababa, Ethiopia)\n"
    word += "=" * 70 + "\n"
    
    return word

def generate_word_cv(data, cv_type):
    """Generate Word format for Master or Minor CV"""
    cv = data.get(cv_type, {})
    
    word = "=" * 80 + "\n"
    word += f"📄 {cv.get('title', 'CV').upper()}\n"
    word += "=" * 80 + "\n"
    word += f"🕐 Generated: {get_ethiopia_time().strftime('%Y-%m-%d %H:%M:%S')} (Addis Ababa, Ethiopia)\n"
    word += f"📅 Last Updated: {cv.get('lastUpdated', 'Never')}\n"
    word += "=" * 80 + "\n\n"
    
    if cv.get('content'):
        word += cv.get('content') + "\n\n"
    
    if cv.get('sections'):
        for section in cv.get('sections', []):
            word += f"\n{'=' * 60}\n"
            word += f"📌 {section.get('title', 'Section')}\n"
            word += f"{'=' * 60}\n"
            word += section.get('content', '') + "\n"
    
    word += "\n" + "=" * 80 + "\n"
    word += "📊 END OF CV\n"
    word += "=" * 80 + "\n"
    
    return word

# ========== LOAD DATA ==========

if 'data' not in st.session_state:
    st.session_state.data = get_data()
    st.session_state.s_saving = False
    st.session_state.j_saving = False
    st.session_state.selected_date = None
    # Store individual word exports as dict
    st.session_state.word_exports = {}

data = st.session_state.data

# ========== SIDEBAR ==========

with st.sidebar:
    st.success("✅ Connected to GitHub!")
    st.write(f"📁 Repository: {REPO}")
    
    st.markdown("---")
    
    st.subheader("📊 Quick Stats")
    st.metric("🎓 Scholarships", len(data.get('scholarships', [])))
    st.metric("💼 Jobs", len(data.get('jobs', [])))
    st.metric("📝 Notes", len(data.get('notes', [])))
    st.metric("📜 History", len(data.get('history', [])))
    
    st.markdown("---")
    st.caption("📦 Data saved on GitHub")
    st.caption(f"🔗 github.com/{USER}/{REPO}")
    st.caption("🇪🇹 Ethiopia Time (UTC+3)")

# ========== 5S DASHBOARD ==========

st.header("🏭 5S Dashboard - Live Status")

active_count = len([s for s in data.get('scholarships', []) if s.get('status') == 'active']) + \
               len([j for j in data.get('jobs', []) if j.get('status') == 'active'])
total_count = len(data.get('scholarships', [])) + len(data.get('jobs', []))
submitted_count = len([s for s in data.get('scholarships', []) if s.get('status') == 'submitted']) + \
                  len([j for j in data.get('jobs', []) if j.get('status') == 'submitted'])
accepted_count = len([s for s in data.get('scholarships', []) if s.get('status') == 'accepted']) + \
                 len([j for j in data.get('jobs', []) if j.get('status') == 'accepted'])
history_count = len(data.get('history', []))

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="ss-sort">
        <b>📋 SORT</b><br>
        <small>Active</small><br>
        <b style="font-size: 2em;">{active_count}</b>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="ss-set">
        <b>📌 SET</b><br>
        <small>Total</small><br>
        <b style="font-size: 2em;">{total_count}</b>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="ss-shine">
        <b>✨ SHINE</b><br>
        <small>Submitted</small><br>
        <b style="font-size: 2em;">{submitted_count}</b>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="ss-standardize">
        <b>📏 STANDARDIZE</b><br>
        <small>Accepted</small><br>
        <b style="font-size: 2em;">{accepted_count}</b>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="ss-sustain">
        <b>♻️ SUSTAIN</b><br>
        <small>History</small><br>
        <b style="font-size: 2em;">{history_count}</b>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ========== PROGRESS CHARTS ==========

st.header("📈 Progress Charts - Submissions Over Time")

# Prepare data for chart
scholarships = data.get('scholarships', [])
jobs = data.get('jobs', [])

# Create dataframe with submission dates
submission_data = []
for s in scholarships:
    if s.get('status') in ['submitted', 'accepted']:
        try:
            date_obj = datetime.strptime(s.get('createdAt', ''), '%Y-%m-%d %H:%M:%S')
            submission_data.append({'date': date_obj, 'type': 'Scholarship'})
        except:
            pass
for j in jobs:
    if j.get('status') in ['submitted', 'accepted']:
        try:
            date_obj = datetime.strptime(j.get('createdAt', ''), '%Y-%m-%d %H:%M:%S')
            submission_data.append({'date': date_obj, 'type': 'Job'})
        except:
            pass

if submission_data:
    df = pd.DataFrame(submission_data)
    df['date'] = pd.to_datetime(df['date'])
    df['day'] = df['date'].dt.date
    
    # Count by day
    daily_counts = df.groupby(['day', 'type']).size().unstack(fill_value=0)
    # Also total per day
    daily_total = df.groupby('day').size()
    
    # Create figure with subplots
    fig = make_subplots(rows=2, cols=1, 
                        subplot_titles=('📊 Submissions Per Day (Scholarships & Jobs)', 
                                        '📈 Cumulative Progress'),
                        vertical_spacing=0.2)
    
    # Line for scholarships per day
    if 'Scholarship' in daily_counts.columns:
        fig.add_trace(
            go.Scatter(x=daily_counts.index, y=daily_counts['Scholarship'],
                       mode='lines+markers', name='Scholarships',
                       line=dict(color='#e94560', width=3),
                       marker=dict(size=8)),
            row=1, col=1
        )
    
    # Line for jobs per day
    if 'Job' in daily_counts.columns:
        fig.add_trace(
            go.Scatter(x=daily_counts.index, y=daily_counts['Job'],
                       mode='lines+markers', name='Jobs',
                       line=dict(color='#00d2ff', width=3),
                       marker=dict(size=8)),
            row=1, col=1
        )
    
    # Cumulative sum
    cumulative = daily_total.cumsum()
    fig.add_trace(
        go.Scatter(x=cumulative.index, y=cumulative.values,
                   mode='lines+markers', name='Total Cumulative',
                   line=dict(color='#28a745', width=4, dash='dash'),
                   marker=dict(size=10)),
        row=2, col=1
    )
    
    fig.update_layout(height=600, showlegend=True,
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Number Submitted", row=1, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Cumulative Total", row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary stats
    total_submitted = len(submission_data)
    total_scholarships_submitted = len([s for s in scholarships if s.get('status') in ['submitted', 'accepted']])
    total_jobs_submitted = len([j for j in jobs if j.get('status') in ['submitted', 'accepted']])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Total Submissions", total_submitted)
    col2.metric("🎓 Scholarships Submitted", total_scholarships_submitted)
    col3.metric("💼 Jobs Submitted", total_jobs_submitted)
else:
    st.info("No submissions yet. Start adding and submitting scholarships/jobs to see progress!")

st.markdown("---")

# ========== CALENDAR ==========

st.header("📅 Calendar - Click Date to Filter")

current_date = get_ethiopia_time()
current_month = current_date.month
current_year = current_date.year

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("◀️ Previous"):
        if current_month == 1:
            current_month = 12
            current_year -= 1
        else:
            current_month -= 1
with col2:
    st.markdown(f"<h3 style='text-align: center;'>{datetime(current_year, current_month, 1).strftime('%B %Y')}</h3>", unsafe_allow_html=True)
with col3:
    if st.button("Next ▶️"):
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1

cal = monthcalendar(current_year, current_month)

days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
cols = st.columns(7)
for i, day in enumerate(days_of_week):
    cols[i].markdown(f"<div style='text-align: center; font-weight: bold;'>{day}</div>", unsafe_allow_html=True)

history_dates = set([h.get('date', '') for h in data.get('history', [])])

for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")
        else:
            date_str = f"{current_year}-{current_month:02d}-{day:02d}"
            is_today = date_str == current_date.strftime("%Y-%m-%d")
            has_items = date_str in history_dates
            is_selected = st.session_state.selected_date == date_str
            
            style = "calendar-day"
            if is_today: style += " today"
            if has_items: style += " has-items"
            if is_selected: style += " selected"
            
            if cols[i].button(str(day), key=f"cal_{date_str}", use_container_width=True):
                if st.session_state.selected_date == date_str:
                    st.session_state.selected_date = None
                else:
                    st.session_state.selected_date = date_str
                st.rerun()

if st.session_state.selected_date:
    selected_date = st.session_state.selected_date
    st.subheader(f"📋 Opportunities for {selected_date}")
    
    matching_scholarships = [s for s in data.get('scholarships', []) if s.get('deadline') == selected_date]
    matching_jobs = [j for j in data.get('jobs', []) if j.get('deadline') == selected_date]
    
    if matching_scholarships or matching_jobs:
        for s in matching_scholarships:
            st.markdown(f"""
            <div class="opportunity-card">
                <b>🎓 {s.get('name', '')}</b><br>
                🏛️ {s.get('uni', 'N/A')} | 🌍 {s.get('country', 'N/A')}<br>
                📊 Status: {s.get('status', 'active')}
            </div>
            """, unsafe_allow_html=True)
        for j in matching_jobs:
            st.markdown(f"""
            <div class="opportunity-card">
                <b>💼 {j.get('title', '')}</b><br>
                🏢 {j.get('company', 'N/A')} | 📍 {j.get('location', 'N/A')}<br>
                📊 Status: {j.get('status', 'active')}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No opportunities with this deadline")
    
    if st.button("Clear Filter"):
        st.session_state.selected_date = None
        st.rerun()
    
    st.markdown("---")

# ========== MASTER CV ==========

st.header("📄 Master CV - Permanent")

master_cv = data.get('masterCV', {})

with st.expander("✏️ Edit Master CV", expanded=False):
    cv_title = st.text_input("CV Title", value=master_cv.get('title', 'ZEDAGIM TESFAYE TANTU - Master CV'))
    cv_content = st.text_area("📝 Paste Your Full CV Content", value=master_cv.get('content', ''), height=300)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Master CV", type="primary"):
            data['masterCV']['title'] = cv_title
            data['masterCV']['content'] = cv_content
            data['masterCV']['lastUpdated'] = get_ethiopia_time().strftime("%Y-%m-%d %H:%M:%S")
            data = add_history(data, "Updated Master CV", "CV", cv_title)
            if save_data(data):
                st.success("✅ Master CV Saved Permanently!")
                time.sleep(0.5)
                st.rerun()
    
    with col2:
        if st.button("📥 Download Master CV", type="secondary"):
            word_content = generate_word_cv(data, "masterCV")
            st.session_state.master_word_export = word_content
            st.rerun()

if master_cv.get('content'):
    st.markdown(f"""
    <div class="cv-master">
        <div style="font-size: 1.5em; font-weight: bold;">{master_cv.get('title', 'Master CV')}</div>
        <div style="opacity: 0.7; font-size: 0.9em;">📅 Last Updated: {master_cv.get('lastUpdated', 'Never')}</div>
        <div style="margin-top: 10px; max-height: 300px; overflow-y: auto; white-space: pre-wrap;">{master_cv.get('content', '')}</div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.get('master_word_export'):
    st.subheader("📋 Master CV - Word Format")
    st.markdown(f"""
    <div class="word-export">
        {st.session_state.master_word_export}
    </div>
    """, unsafe_allow_html=True)
    st.info("📋 Select all text above and press Ctrl+C to copy")
    if st.button("Clear Master CV Export"):
        del st.session_state.master_word_export
        st.rerun()

st.markdown("---")

# ========== MINOR CV ==========

st.header("📄 Minor CV - Permanent")

minor_cv = data.get('minorCV', {})

with st.expander("✏️ Edit Minor CV", expanded=False):
    minor_title = st.text_input("Minor CV Title", value=minor_cv.get('title', 'ZEDAGIM TESFAYE TANTU - Minor CV'))
    minor_content = st.text_area("📝 Paste Your Minor CV Content", value=minor_cv.get('content', ''), height=300)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Minor CV", type="primary"):
            data['minorCV']['title'] = minor_title
            data['minorCV']['content'] = minor_content
            data['minorCV']['lastUpdated'] = get_ethiopia_time().strftime("%Y-%m-%d %H:%M:%S")
            data = add_history(data, "Updated Minor CV", "CV", minor_title)
            if save_data(data):
                st.success("✅ Minor CV Saved Permanently!")
                time.sleep(0.5)
                st.rerun()
    
    with col2:
        if st.button("📥 Download Minor CV", type="secondary"):
            word_content = generate_word_cv(data, "minorCV")
            st.session_state.minor_word_export = word_content
            st.rerun()

if minor_cv.get('content'):
    st.markdown(f"""
    <div class="cv-minor">
        <div style="font-size: 1.5em; font-weight: bold;">{minor_cv.get('title', 'Minor CV')}</div>
        <div style="opacity: 0.7; font-size: 0.9em;">📅 Last Updated: {minor_cv.get('lastUpdated', 'Never')}</div>
        <div style="margin-top: 10px; max-height: 300px; overflow-y: auto; white-space: pre-wrap;">{minor_cv.get('content', '')}</div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.get('minor_word_export'):
    st.subheader("📋 Minor CV - Word Format")
    st.markdown(f"""
    <div class="word-export">
        {st.session_state.minor_word_export}
    </div>
    """, unsafe_allow_html=True)
    st.info("📋 Select all text above and press Ctrl+C to copy")
    if st.button("Clear Minor CV Export"):
        del st.session_state.minor_word_export
        st.rerun()

st.markdown("---")

# ========== QUICK ADD CV SECTIONS ==========

st.subheader("➕ Quick Add to Both CVs")

with st.expander("Add Experience/Section to CVs", expanded=False):
    section_title = st.text_input("Section Title", placeholder="e.g., Maritime GeoAI System")
    section_content = st.text_area("Section Content", height=150, placeholder="Describe your achievement...")
    cv_choice = st.radio("Add to:", ["Both CVs", "Master CV Only", "Minor CV Only"])
    
    if st.button("➕ Add Section", type="primary"):
        if section_title and section_content:
            new_section = {
                "title": section_title,
                "content": section_content,
                "added": get_ethiopia_time().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if cv_choice in ["Both CVs", "Master CV Only"]:
                if 'sections' not in data['masterCV']:
                    data['masterCV']['sections'] = []
                data['masterCV']['sections'].append(new_section)
                data['masterCV']['lastUpdated'] = get_ethiopia_time().strftime("%Y-%m-%d %H:%M:%S")
            
            if cv_choice in ["Both CVs", "Minor CV Only"]:
                if 'sections' not in data['minorCV']:
                    data['minorCV']['sections'] = []
                data['minorCV']['sections'].append(new_section)
                data['minorCV']['lastUpdated'] = get_ethiopia_time().strftime("%Y-%m-%d %H:%M:%S")
            
            data = add_history(data, "Added CV Section", "CV", section_title)
            if save_data(data):
                st.success(f"✅ Section '{section_title}' Added!")
                time.sleep(0.5)
                st.rerun()
        else:
            st.error("❌ Title and Content are required!")

# ========== SCHOLARSHIPS ==========

st.header("🎓 Scholarships")

with st.expander("➕ Add New Scholarship", expanded=False):
    if not st.session_state.get('s_saving', False):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Scholarship Name *", key="s_name")
            uni = st.text_input("University/Organization", key="s_uni")
        with col2:
            deadline = st.date_input("Deadline *", key="s_deadline")
            country = st.text_input("Country", key="s_country")
        
        notes = st.text_area("📝 Notes", key="s_notes", height=80)
        link = st.text_input("🔗 Application Link", key="s_link")
        
        if st.button("💾 Save Scholarship", type="primary", key="save_s"):
            if name and deadline:
                existing = [s for s in data.get('scholarships', []) if s.get('name', '').lower() == name.lower()]
                if existing:
                    st.error(f"❌ DUPLICATE! '{name}' already exists!")
                else:
                    st.session_state.s_saving = True
                    new_s = {
                        "id": str(datetime.now().timestamp()),
                        "name": name,
                        "uni": uni or "",
                        "deadline": deadline.strftime("%Y-%m-%d"),
                        "country": country or "",
                        "notes": notes or "",
                        "link": link or "",
                        "status": "active",
                        "createdAt": get_ethiopia_time().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    data['scholarships'].append(new_s)
                    data = add_history(data, "Added", "Scholarship", name)
                    if save_data(data):
                        st.success(f"✅ '{name}' Saved Permanently!")
                        time.sleep(1)
                        st.session_state.s_saving = False
                        st.rerun()
            else:
                st.error("❌ Name and Deadline are required!")
    else:
        st.info("⏳ Saving... Please wait")
        time.sleep(1)
        st.session_state.s_saving = False
        st.rerun()

# Display Scholarships
scholarships = data.get('scholarships', [])
if scholarships:
    st.subheader(f"📋 Your Scholarships ({len(scholarships)})")
    sorted_items = sorted(scholarships, key=lambda x: x.get('deadline', '9999-12-31'))
    
    for idx, s in enumerate(sorted_items):
        days_left = 0
        try:
            if s.get('deadline'):
                deadline = datetime.strptime(s.get('deadline'), '%Y-%m-%d')
                days_left = (deadline - datetime.now()).days
        except:
            pass
        
        if days_left <= 5 and days_left >= 0:
            status_class = "deadline-red"
            status_label = f"🔴 {days_left} days left - URGENT!"
        elif days_left <= 20:
            status_class = "deadline-yellow"
            status_label = f"🟡 {days_left} days left"
        elif days_left > 20:
            status_class = "deadline-green"
            status_label = f"🟢 {days_left} days left"
        else:
            status_class = "deadline-red"
            status_label = "⏰ EXPIRED"
        
        with st.container():
            col1, col2, col3, col4 = st.columns([2.5, 1.5, 1, 1])
            with col1:
                st.markdown(f"**{s.get('name', '')}**")
                if s.get('uni'): st.caption(f"🏛️ {s.get('uni')}")
                if s.get('country'): st.caption(f"🌍 {s.get('country')}")
                if s.get('notes'): st.caption(f"📝 {s.get('notes')[:80]}")
            with col2:
                st.write(f"📅 {s.get('deadline', 'No deadline')}")
                st.markdown(f"<span class='{status_class}'>{status_label}</span>", unsafe_allow_html=True)
                status = s.get('status', 'active')
                icons = {"active": "🟢 Active", "submitted": "📤 Submitted", "accepted": "✅ Accepted", "rejected": "❌ Rejected"}
                st.write(icons.get(status, status))
            with col3:
                # Individual Word Export
                key = f"word_s_{idx}"
                if st.button("📄 Word", key=f"s_word_{idx}", help="Export this scholarship to Word format"):
                    st.session_state.word_exports[key] = generate_individual_word(s, "scholarship")
                    st.rerun()
                if s.get('status') == 'active':
                    if st.button("📤 Submit", key=f"s_sub_{idx}"):
                        s['status'] = 'submitted'
                        data = add_history(data, "Submitted", "Scholarship", s.get('name'))
                        save_data(data)
                        st.rerun()
            with col4:
                if s.get('status') == 'submitted':
                    if st.button("✅ Accept", key=f"s_acc_{idx}"):
                        s['status'] = 'accepted'
                        data = add_history(data, "Accepted", "Scholarship", s.get('name'))
                        save_data(data)
                        st.rerun()
                    if st.button("❌ Reject", key=f"s_rej_{idx}"):
                        s['status'] = 'rejected'
                        data = add_history(data, "Rejected", "Scholarship", s.get('name'))
                        save_data(data)
                        st.rerun()
                if st.button("🗑️ Delete", key=f"s_del_{idx}"):
                    data['scholarships'].remove(s)
                    data = add_history(data, "Deleted", "Scholarship", s.get('name'))
                    save_data(data)
                    st.rerun()
            
            # Show individual word export if exists
            if key in st.session_state.word_exports:
                st.markdown(f"""
                <div class="word-export">
                    {st.session_state.word_exports[key]}
                </div>
                """, unsafe_allow_html=True)
                st.info("📋 Select all text above and press Ctrl+C to copy")
                if st.button("Clear", key=f"clear_s_{idx}"):
                    del st.session_state.word_exports[key]
                    st.rerun()
            
            st.divider()

st.markdown("---")

# ========== JOBS ==========

st.header("💼 Jobs")

with st.expander("➕ Add New Job", expanded=False):
    if not st.session_state.get('j_saving', False):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Job Title *", key="j_title")
            company = st.text_input("Company *", key="j_company")
        with col2:
            deadline = st.date_input("Deadline *", key="j_deadline")
            location = st.text_input("Location", key="j_location")
        
        notes = st.text_area("📝 Notes", key="j_notes", height=80)
        link = st.text_input("🔗 Application Link", key="j_link")
        
        if st.button("💾 Save Job", type="primary", key="save_j"):
            if title and company and deadline:
                existing = [j for j in data.get('jobs', []) if j.get('title', '').lower() == title.lower()]
                if existing:
                    st.error(f"❌ DUPLICATE! '{title}' already exists!")
                else:
                    st.session_state.j_saving = True
                    new_j = {
                        "id": str(datetime.now().timestamp()),
                        "title": title,
                        "company": company,
                        "deadline": deadline.strftime("%Y-%m-%d"),
                        "location": location or "",
                        "notes": notes or "",
                        "link": link or "",
                        "status": "active",
                        "createdAt": get_ethiopia_time().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    data['jobs'].append(new_j)
                    data = add_history(data, "Added", "Job", title)
                    if save_data(data):
                        st.success(f"✅ '{title}' Saved Permanently!")
                        time.sleep(1)
                        st.session_state.j_saving = False
                        st.rerun()
            else:
                st.error("❌ Title, Company, and Deadline are required!")
    else:
        st.info("⏳ Saving... Please wait")
        time.sleep(1)
        st.session_state.j_saving = False
        st.rerun()

# Display Jobs
jobs = data.get('jobs', [])
if jobs:
    st.subheader(f"📋 Your Jobs ({len(jobs)})")
    sorted_items = sorted(jobs, key=lambda x: x.get('deadline', '9999-12-31'))
    
    for idx, j in enumerate(sorted_items):
        days_left = 0
        try:
            if j.get('deadline'):
                deadline = datetime.strptime(j.get('deadline'), '%Y-%m-%d')
                days_left = (deadline - datetime.now()).days
        except:
            pass
        
        if days_left <= 5 and days_left >= 0:
            status_class = "deadline-red"
            status_label = f"🔴 {days_left} days left - URGENT!"
        elif days_left <= 20:
            status_class = "deadline-yellow"
            status_label = f"🟡 {days_left} days left"
        elif days_left > 20:
            status_class = "deadline-green"
            status_label = f"🟢 {days_left} days left"
        else:
            status_class = "deadline-red"
            status_label = "⏰ EXPIRED"
        
        with st.container():
            col1, col2, col3, col4 = st.columns([2.5, 1.5, 1, 1])
            with col1:
                st.markdown(f"**{j.get('title', '')}**")
                if j.get('company'): st.caption(f"🏢 {j.get('company')}")
                if j.get('location'): st.caption(f"📍 {j.get('location')}")
                if j.get('notes'): st.caption(f"📝 {j.get('notes')[:80]}")
            with col2:
                st.write(f"📅 {j.get('deadline', 'No deadline')}")
                st.markdown(f"<span class='{status_class}'>{status_label}</span>", unsafe_allow_html=True)
                status = j.get('status', 'active')
                icons = {"active": "🟢 Active", "submitted": "📤 Submitted", "accepted": "✅ Accepted", "rejected": "❌ Rejected"}
                st.write(icons.get(status, status))
            with col3:
                key = f"word_j_{idx}"
                if st.button("📄 Word", key=f"j_word_{idx}", help="Export this job to Word format"):
                    st.session_state.word_exports[key] = generate_individual_word(j, "job")
                    st.rerun()
                if j.get('status') == 'active':
                    if st.button("📤 Submit", key=f"j_sub_{idx}"):
                        j['status'] = 'submitted'
                        data = add_history(data, "Submitted", "Job", j.get('title'))
                        save_data(data)
                        st.rerun()
            with col4:
                if j.get('status') == 'submitted':
                    if st.button("✅ Accept", key=f"j_acc_{idx}"):
                        j['status'] = 'accepted'
                        data = add_history(data, "Accepted", "Job", j.get('title'))
                        save_data(data)
                        st.rerun()
                    if st.button("❌ Reject", key=f"j_rej_{idx}"):
                        j['status'] = 'rejected'
                        data = add_history(data, "Rejected", "Job", j.get('title'))
                        save_data(data)
                        st.rerun()
                if st.button("🗑️ Delete", key=f"j_del_{idx}"):
                    data['jobs'].remove(j)
                    data = add_history(data, "Deleted", "Job", j.get('title'))
                    save_data(data)
                    st.rerun()
            
            if key in st.session_state.word_exports:
                st.markdown(f"""
                <div class="word-export">
                    {st.session_state.word_exports[key]}
                </div>
                """, unsafe_allow_html=True)
                st.info("📋 Select all text above and press Ctrl+C to copy")
                if st.button("Clear", key=f"clear_j_{idx}"):
                    del st.session_state.word_exports[key]
                    st.rerun()
            
            st.divider()

st.markdown("---")

# ========== NOTES ==========

st.header("📝 Quick Notes")

with st.expander("➕ Add New Note", expanded=False):
    note_content = st.text_area("📝 Write your note here", height=150, key="note_input")
    
    if st.button("💾 Save Note", type="primary"):
        if note_content:
            if 'notes' not in data: data['notes'] = []
            data['notes'].append({
                "id": str(datetime.now().timestamp()),
                "content": note_content,
                "timestamp": get_ethiopia_time().strftime("%Y-%m-%d %H:%M:%S")
            })
            data = add_history(data, "Added Note", "Note", note_content[:30] + "...")
            if save_data(data):
                st.success("✅ Note Saved Permanently!")
                time.sleep(0.5)
                st.rerun()
        else:
            st.error("❌ Please enter some text!")

notes = data.get('notes', [])
if notes:
    st.subheader(f"📋 Your Notes ({len(notes)})")
    for idx, n in enumerate(reversed(notes)):
        with st.container():
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"""
                <div class="note-card">
                    <b>📝 {n.get('content', '')}</b><br>
                    <small>🕐 {n.get('timestamp', '')}</small>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("🗑️", key=f"note_del_{idx}"):
                    data['notes'].remove(n)
                    save_data(data)
                    st.rerun()

st.markdown("---")

# ========== HISTORY ==========

st.header("📜 Complete History Log")

if st.button("📄 Export Full History as Word"):
    eth_time = get_ethiopia_time()
    full_history = "📜 COMPLETE HISTORY LOG\n"
    full_history += "=" * 70 + "\n"
    full_history += f"📅 Generated: {eth_time.strftime('%Y-%m-%d %H:%M:%S')} (Addis Ababa, Ethiopia)\n"
    full_history += "=" * 70 + "\n\n"
    
    if data.get('history'):
        for h in reversed(data['history']):
            full_history += f"🕐 {h.get('timestamp', '')}\n"
            full_history += f"📌 {h.get('action', '')}: {h.get('name', '')}\n"
            if h.get('details'): full_history += f"📝 {h.get('details')}\n"
            full_history += "-" * 40 + "\n"
    else:
        full_history += "No history yet.\n"
    
    full_history += "\n" + "=" * 70 + "\n"
    full_history += f"Total Actions: {len(data.get('history', []))}\n"
    full_history += "=" * 70 + "\n"
    
    st.session_state.full_history_export = full_history
    st.rerun()

if st.session_state.get('full_history_export'):
    st.subheader("📋 Full History - Word Format")
    st.markdown(f"""
    <div class="word-export">
        {st.session_state.full_history_export}
    </div>
    """, unsafe_allow_html=True)
    st.info("📋 Select all text above and press Ctrl+C to copy")
    if st.button("Clear History Export"):
        del st.session_state.full_history_export
        st.rerun()

if data.get('history'):
    st.subheader("📋 History Timeline")
    for h in reversed(data['history'][-30:]):
        emoji = {"Added": "➕", "Submitted": "📤", "Accepted": "✅", "Rejected": "❌", "Deleted": "🗑️", "Updated Master CV": "📄", "Updated Minor CV": "📄", "Added CV Section": "📌"}.get(h.get('action', ''), "📌")
        st.markdown(f"""
        <div class="history-item">
            <b>{emoji} {h.get('action', '')}</b> {h.get('type', '')}: <b>{h.get('name', '')}</b>
            <br><small>🕐 {h.get('timestamp', '')}</small>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No history yet")

# ========== FOOTER ==========

st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🇪🇹 Built for Ethiopian scholars")
with col2:
    st.caption("📦 Data saved permanently on GitHub")
with col3:
    st.caption(f"🔗 github.com/{USER}/{REPO}")

st.caption("✅ Zero-duplication | 🔒 Button lock | 📊 Live Dashboard | 💾 Permanent storage | 🇪🇹 Ethiopia Time")
