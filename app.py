import streamlit as st
import requests
import json
import base64
from datetime import datetime, timedelta
import time
import pandas as pd
from calendar import monthcalendar

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

# ========== CUSTOM CSS ==========

st.markdown("""
<style>
    .welcome-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        margin: 10px 0 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .welcome-title { font-size: 2.2em; font-weight: bold; }
    .welcome-time { font-size: 1.5em; opacity: 0.9; }
    .welcome-date { font-size: 1.2em; opacity: 0.8; }
    
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
    .cv-section-title {
        color: #e94560;
        font-weight: bold;
        font-size: 1.2em;
    }
    .cv-minor-title {
        color: #00d2ff;
        font-weight: bold;
        font-size: 1.2em;
    }
    .cv-item {
        padding: 8px 12px;
        margin: 5px 0;
        background: rgba(255,255,255,0.03);
        border-radius: 8px;
        border-left: 3px solid #e94560;
    }
    .cv-item-minor {
        border-left: 3px solid #00d2ff;
    }
    
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
    
    .download-btn {
        background: #28a745;
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
    }
    .download-btn:hover { background: #218838; transform: scale(1.05); }
    
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
</style>
""", unsafe_allow_html=True)

# ========== WELCOME SECTION ==========

current_time = datetime.now()
day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_name = day_names[current_time.weekday()]

st.markdown(f"""
<div class="welcome-box">
    <div class="welcome-title">🦸 Welcome, Superhero Dagim!</div>
    <div class="welcome-time">🕐 {current_time.strftime('%I:%M:%S %p')}</div>
    <div class="welcome-date">📅 {current_time.strftime('%B %d, %Y')} - {day_name}</div>
    <div style="margin-top: 5px; opacity: 0.7; font-size: 0.9em;">📍 Time Zone: {time.tzname[0]}</div>
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
                data['masterCV'] = {
                    "title": "ZEDAGIM TESFAYE TANTU - Master CV",
                    "content": "",
                    "lastUpdated": "",
                    "sections": []
                }
            if 'minorCV' not in data:
                data['minorCV'] = {
                    "title": "ZEDAGIM TESFAYE TANTU - Minor CV",
                    "content": "",
                    "lastUpdated": "",
                    "sections": []
                }
            if 'history' not in data: data['history'] = []
            if 'notes' not in data: data['notes'] = []
            return data
        else:
            default_data = {
                "scholarships": [], 
                "jobs": [], 
                "masterCV": {"title": "ZEDAGIM TESFAYE TANTU - Master CV", "content": "", "lastUpdated": "", "sections": []},
                "minorCV": {"title": "ZEDAGIM TESFAYE TANTU - Minor CV", "content": "", "lastUpdated": "", "sections": []},
                "history": [], 
                "notes": []
            }
            save_data(default_data)
            return default_data
    except:
        return {
            "scholarships": [], 
            "jobs": [], 
            "masterCV": {"title": "ZEDAGIM TESFAYE TANTU - Master CV", "content": "", "lastUpdated": "", "sections": []},
            "minorCV": {"title": "ZEDAGIM TESFAYE TANTU - Minor CV", "content": "", "lastUpdated": "", "sections": []},
            "history": [], 
            "notes": []
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
    data['history'].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "action": action,
        "type": item_type,
        "name": item_name,
        "details": details
    })
    return data

def generate_word_cv(data, cv_type="master"):
    """Generate Word format CV"""
    cv = data.get(cv_type, {})
    
    word = "=" * 80 + "\n"
    word += f"📄 {cv.get('title', 'CV').upper()}\n"
    word += "=" * 80 + "\n"
    word += f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    word += f"📅 Last Updated: {cv.get('lastUpdated', 'Never')}\n"
    word += "=" * 80 + "\n\n"
    
    # Content
    if cv.get('content'):
        word += cv.get('content') + "\n\n"
    
    # Sections
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
            data['masterCV']['lastUpdated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = add_history(data, "Updated Master CV", "CV", cv_title)
            if save_data(data):
                st.success("✅ Master CV Saved Permanently!")
                time.sleep(0.5)
                st.rerun()
    
    with col2:
        if st.button("📥 Download Master CV as Word", type="secondary"):
            word_content = generate_word_cv(data, "masterCV")
            st.session_state.master_word_export = word_content
            st.rerun()

# Show Master CV
if master_cv.get('content'):
    st.markdown(f"""
    <div class="cv-master">
        <div style="font-size: 1.5em; font-weight: bold;">{master_cv.get('title', 'Master CV')}</div>
        <div style="opacity: 0.7; font-size: 0.9em;">📅 Last Updated: {master_cv.get('lastUpdated', 'Never')}</div>
        <div style="margin-top: 10px; max-height: 300px; overflow-y: auto; white-space: pre-wrap;">{master_cv.get('content', '')}</div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.get('master_word_export'):
    st.subheader("📋 Master CV - Word Format (Copy & Paste)")
    st.markdown(f"""
    <div class="word-export">
        {st.session_state.master_word_export}
    </div>
    """, unsafe_allow_html=True)
    st.info("📋 Select all text above and press Ctrl+C to copy")

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
            data['minorCV']['lastUpdated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = add_history(data, "Updated Minor CV", "CV", minor_title)
            if save_data(data):
                st.success("✅ Minor CV Saved Permanently!")
                time.sleep(0.5)
                st.rerun()
    
    with col2:
        if st.button("📥 Download Minor CV as Word", type="secondary"):
            word_content = generate_word_cv(data, "minorCV")
            st.session_state.minor_word_export = word_content
            st.rerun()

# Show Minor CV
if minor_cv.get('content'):
    st.markdown(f"""
    <div class="cv-minor">
        <div style="font-size: 1.5em; font-weight: bold;">{minor_cv.get('title', 'Minor CV')}</div>
        <div style="opacity: 0.7; font-size: 0.9em;">📅 Last Updated: {minor_cv.get('lastUpdated', 'Never')}</div>
        <div style="margin-top: 10px; max-height: 300px; overflow-y: auto; white-space: pre-wrap;">{minor_cv.get('content', '')}</div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.get('minor_word_export'):
    st.subheader("📋 Minor CV - Word Format (Copy & Paste)")
    st.markdown(f"""
    <div class="word-export">
        {st.session_state.minor_word_export}
    </div>
    """, unsafe_allow_html=True)
    st.info("📋 Select all text above and press Ctrl+C to copy")

st.markdown("---")

# ========== QUICK ADD CV SECTIONS ==========

st.subheader("➕ Quick Add to Both CVs")

with st.expander("Add Experience/Section to Both CVs", expanded=False):
    section_title = st.text_input("Section Title", placeholder="e.g., Maritime GeoAI System")
    section_content = st.text_area("Section Content", height=150, placeholder="Describe your achievement or experience...")
    cv_choice = st.radio("Add to:", ["Both CVs", "Master CV Only", "Minor CV Only"])
    
    if st.button("➕ Add Section", type="primary"):
        if section_title and section_content:
            new_section = {
                "title": section_title,
                "content": section_content,
                "added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if cv_choice in ["Both CVs", "Master CV Only"]:
                if 'sections' not in data['masterCV']:
                    data['masterCV']['sections'] = []
                data['masterCV']['sections'].append(new_section)
                data['masterCV']['lastUpdated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if cv_choice in ["Both CVs", "Minor CV Only"]:
                if 'sections' not in data['minorCV']:
                    data['minorCV']['sections'] = []
                data['minorCV']['sections'].append(new_section)
                data['minorCV']['lastUpdated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            data = add_history(data, "Added CV Section", "CV", section_title)
            if save_data(data):
                st.success(f"✅ Section '{section_title}' Added Permanently!")
                time.sleep(0.5)
                st.rerun()
        else:
            st.error("❌ Title and Content are required!")

# ========== SHOW CV SECTIONS ==========

if data['masterCV'].get('sections') or data['minorCV'].get('sections'):
    st.subheader("📋 CV Sections")
    
    tab1, tab2 = st.tabs(["Master CV Sections", "Minor CV Sections"])
    
    with tab1:
        if data['masterCV'].get('sections'):
            for section in data['masterCV']['sections']:
                st.markdown(f"""
                <div class="cv-section">
                    <div class="cv-section-title">📌 {section.get('title', '')}</div>
                    <div style="margin-top: 5px; white-space: pre-wrap;">{section.get('content', '')}</div>
                    <div style="opacity: 0.5; font-size: 0.8em;">Added: {section.get('added', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No sections in Master CV yet")
    
    with tab2:
        if data['minorCV'].get('sections'):
            for section in data['minorCV']['sections']:
                st.markdown(f"""
                <div class="cv-section">
                    <div class="cv-minor-title">📌 {section.get('title', '')}</div>
                    <div style="margin-top: 5px; white-space: pre-wrap;">{section.get('content', '')}</div>
                    <div style="opacity: 0.5; font-size: 0.8em;">Added: {section.get('added', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No sections in Minor CV yet")

st.markdown("---")

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
                # Check for duplicates
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
                        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{s.get('name', '')}**")
                if s.get('uni'): st.caption(f"🏛️ {s.get('uni')}")
                if s.get('country'): st.caption(f"🌍 {s.get('country')}")
                if s.get('notes'): st.caption(f"📝 {s.get('notes')[:100]}")
            with col2:
                st.write(f"📅 {s.get('deadline', 'No deadline')}")
                st.markdown(f"<span class='{status_class}'>{status_label}</span>", unsafe_allow_html=True)
                status = s.get('status', 'active')
                icons = {"active": "🟢 Active", "submitted": "📤 Submitted", "accepted": "✅ Accepted", "rejected": "❌ Rejected"}
                st.write(icons.get(status, status))
            with col3:
                if s.get('status') == 'active':
                    if st.button("📤 Submit", key=f"s_sub_{idx}"):
                        s['status'] = 'submitted'
                        data = add_history(data, "Submitted", "Scholarship", s.get('name'))
                        save_data(data)
                        st.rerun()
                elif s.get('status') == 'submitted':
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
                        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{j.get('title', '')}**")
                if j.get('company'): st.caption(f"🏢 {j.get('company')}")
                if j.get('location'): st.caption(f"📍 {j.get('location')}")
                if j.get('notes'): st.caption(f"📝 {j.get('notes')[:100]}")
            with col2:
                st.write(f"📅 {j.get('deadline', 'No deadline')}")
                st.markdown(f"<span class='{status_class}'>{status_label}</span>", unsafe_allow_html=True)
                status = j.get('status', 'active')
                icons = {"active": "🟢 Active", "submitted": "📤 Submitted", "accepted": "✅ Accepted", "rejected": "❌ Rejected"}
                st.write(icons.get(status, status))
            with col3:
                if j.get('status') == 'active':
                    if st.button("📤 Submit", key=f"j_sub_{idx}"):
                        j['status'] = 'submitted'
                        data = add_history(data, "Submitted", "Job", j.get('title'))
                        save_data(data)
                        st.rerun()
                elif j.get('status') == 'submitted':
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
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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

if st.button("📄 Export All History as Word"):
    full_history = "📜 COMPLETE HISTORY\n"
    full_history += "=" * 60 + "\n"
    for h in reversed(data.get('history', [])):
        full_history += f"{h.get('timestamp', '')} - {h.get('action', '')}: {h.get('name', '')}\n"
        if h.get('details'): full_history += f"  Details: {h.get('details')}\n"
    full_history += "=" * 60 + "\n"
    full_history += f"Total: {len(data.get('history', []))} actions"
    st.session_state.full_history_export = full_history
    st.rerun()

if st.session_state.get('full_history_export'):
    st.markdown(f"""
    <div class="word-export">
        {st.session_state.full_history_export}
    </div>
    """, unsafe_allow_html=True)
    st.info("📋 Select text above and press Ctrl+C to copy")

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

st.caption("✅ Zero-duplication | 🔒 Button lock | 📊 5S Dashboard | 💾 Permanent storage")
