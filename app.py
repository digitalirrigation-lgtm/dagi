import streamlit as st
import requests
import json
import base64
from datetime import datetime, timedelta
import time
import pandas as pd

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
    page_title="📚 Dagi Tracker Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========

st.markdown("""
<style>
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
        min-height: 300px;
        max-height: 600px;
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
    
    .button-locked {
        opacity: 0.5;
        pointer-events: none;
    }
    
    .stButton button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .success-box {
        padding: 12px;
        background: #d4edda;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 10px 0;
    }
    .danger-box {
        padding: 12px;
        background: #f8d7da;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 10px 0;
    }
    
    .stats-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border: 2px solid #e9ecef;
    }
    .stats-number { font-size: 2.5em; font-weight: bold; color: #007bff; }
    .stats-label { color: #6c757d; font-size: 0.9em; }
</style>
""", unsafe_allow_html=True)

st.title("📚 My Scholarship & Job Tracker Pro")
st.caption("🔒 Zero-Duplication | 💾 Permanent GitHub Storage | 📊 Live Dashboard")

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
            if 'masterCV' not in data: data['masterCV'] = {"title": "My Master CV", "content": "", "lastUpdated": ""}
            if 'history' not in data: data['history'] = []
            if 'notes' not in data: data['notes'] = []
            return data
        else:
            default_data = {"scholarships": [], "jobs": [], "masterCV": {"title": "My Master CV", "content": "", "lastUpdated": ""}, "history": [], "notes": []}
            save_data(default_data)
            return default_data
    except:
        return {"scholarships": [], "jobs": [], "masterCV": {"title": "My Master CV", "content": "", "lastUpdated": ""}, "history": [], "notes": []}

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
        "action": action,
        "type": item_type,
        "name": item_name,
        "details": details
    })
    return data

def check_duplicate(data, item_type, name):
    items = data.get(item_type, [])
    for item in items:
        if item.get('name', '').lower() == name.lower():
            return True
    return False

def get_deadline_status(deadline_str):
    if not deadline_str:
        return {"label": "No deadline", "class": "deadline-green"}
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        days_left = (deadline - datetime.now()).days
        if days_left < 0:
            return {"label": f"⏰ EXPIRED ({abs(days_left)} days ago)", "class": "deadline-red"}
        elif days_left <= 5:
            return {"label": f"🔴 {days_left} days left - URGENT!", "class": "deadline-red"}
        elif days_left <= 20:
            return {"label": f"🟡 {days_left} days left", "class": "deadline-yellow"}
        else:
            return {"label": f"🟢 {days_left} days left", "class": "deadline-green"}
    except:
        return {"label": "Invalid date", "class": "deadline-green"}

# ========== LOAD DATA ==========

if 'data' not in st.session_state:
    st.session_state.data = get_data()
    st.session_state.s_saving = False
    st.session_state.j_saving = False

data = st.session_state.data

# ========== SIDEBAR ==========

with st.sidebar:
    st.success("✅ Connected to GitHub!")
    st.write(f"📁 Repository: {REPO}")
    
    st.markdown("---")
    
    st.subheader("📊 Quick Stats")
    total_s = len(data.get('scholarships', []))
    total_j = len(data.get('jobs', []))
    st.metric("🎓 Scholarships", total_s)
    st.metric("💼 Jobs", total_j)
    st.metric("📝 Notes", len(data.get('notes', [])))
    
    st.markdown("---")
    
    st.subheader("📜 Recent History")
    history = data.get('history', [])
    if history:
        for h in history[-3:]:
            st.markdown(f"""
            <div class="history-item">
                <small>{h.get('timestamp', '')[:16]}</small><br>
                <b>{h.get('action', '')}</b> {h.get('name', '')}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("📦 Data saved on GitHub")
    st.caption(f"🔗 github.com/{USER}/{REPO}")

# ========== 5S DASHBOARD - DYNAMIC ==========

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
        <small>Active Items</small><br>
        <b style="font-size: 2em;">{active_count}</b>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="ss-set">
        <b>📌 SET</b><br>
        <small>Total Items</small><br>
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

# ========== PROGRESS DASHBOARD ==========

st.subheader("📊 Progress Dashboard")

if total_count > 0:
    col1, col2, col3, col4 = st.columns(4)
    completion = int((submitted_count + accepted_count) / total_count * 100) if total_count > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{total_count}</div>
            <div class="stats-label">📊 Total Items</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{completion}%</div>
            <div class="stats-label">✅ Completion Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pending = total_count - submitted_count - accepted_count
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{pending}</div>
            <div class="stats-label">⏳ Pending</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{accepted_count}</div>
            <div class="stats-label">🎯 Achieved</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress bar
    st.progress(completion / 100)
    st.caption(f"📈 Progress: {completion}% complete")

st.markdown("---")

# ========== WORD FORMAT EXPORT ==========

st.header("📄 Word Format Export - Copy & Paste Ready")

col1, col2 = st.columns([2, 1])

with col1:
    if st.button("📝 Generate Full Report", type="primary", use_container_width=True):
        word_content = "=" * 60 + "\n"
        word_content += "📚 SCHOLARSHIP & JOB TRACKER REPORT\n"
        word_content += f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        word_content += "=" * 60 + "\n\n"
        
        word_content += "🎓 SCHOLARSHIPS\n"
        word_content += "-" * 40 + "\n"
        if data.get('scholarships'):
            for s in data['scholarships']:
                word_content += f"• {s.get('name', '')}\n"
                word_content += f"  University: {s.get('uni', 'N/A')}\n"
                word_content += f"  Deadline: {s.get('deadline', 'N/A')}\n"
                word_content += f"  Status: {s.get('status', 'active')}\n"
                if s.get('notes'): word_content += f"  Notes: {s.get('notes')}\n"
                word_content += "\n"
        else:
            word_content += "No scholarships added yet.\n\n"
        
        word_content += "💼 JOBS\n"
        word_content += "-" * 40 + "\n"
        if data.get('jobs'):
            for j in data['jobs']:
                word_content += f"• {j.get('title', '')}\n"
                word_content += f"  Company: {j.get('company', 'N/A')}\n"
                word_content += f"  Deadline: {j.get('deadline', 'N/A')}\n"
                word_content += f"  Status: {j.get('status', 'active')}\n"
                if j.get('notes'): word_content += f"  Notes: {j.get('notes')}\n"
                word_content += "\n"
        else:
            word_content += "No jobs added yet.\n\n"
        
        word_content += "📝 NOTES\n"
        word_content += "-" * 40 + "\n"
        if data.get('notes'):
            for n in data['notes']:
                word_content += f"• {n.get('content', '')}\n"
                word_content += f"  Added: {n.get('timestamp', '')}\n\n"
        else:
            word_content += "No notes added yet.\n\n"
        
        word_content += "📜 HISTORY LOG\n"
        word_content += "-" * 40 + "\n"
        if data.get('history'):
            for h in data['history']:
                word_content += f"{h.get('timestamp', '')} - {h.get('action', '')}: {h.get('name', '')}\n"
        else:
            word_content += "No history yet.\n"
        
        word_content += "\n" + "=" * 60 + "\n"
        word_content += "📊 SUMMARY STATISTICS\n"
        word_content += "=" * 60 + "\n"
        word_content += f"Total Scholarships: {len(data.get('scholarships', []))}\n"
        word_content += f"Total Jobs: {len(data.get('jobs', []))}\n"
        word_content += f"Total Notes: {len(data.get('notes', []))}\n"
        word_content += f"Total Actions: {len(data.get('history', []))}\n"
        word_content += f"Active: {active_count}\n"
        word_content += f"Submitted: {submitted_count}\n"
        word_content += f"Accepted: {accepted_count}\n"
        
        st.session_state.word_content = word_content
        st.rerun()

with col2:
    if st.button("📋 Copy All", type="secondary", use_container_width=True):
        st.info("✅ Ready to copy! Select all text below and press Ctrl+C")

if 'word_content' in st.session_state:
    st.markdown("---")
    st.subheader("📋 Your Report (Select all and Copy)")
    st.markdown(f"""
    <div class="word-export" id="word-content">
        {st.session_state.word_content}
    </div>
    """, unsafe_allow_html=True)
    st.caption("💡 Tip: Click inside the box, press Ctrl+A to select all, then Ctrl+C to copy")

st.markdown("---")

# ========== NOTES SECTION ==========

st.header("📝 Quick Notes - Save Everything")

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

# Display notes
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
else:
    st.info("No notes yet. Add your first note above!")

st.markdown("---")

# ========== MASTER CV ==========

st.header("📄 Master CV")

with st.expander("✏️ Edit Your Master CV", expanded=False):
    cv_title = st.text_input("CV Title", value=data.get('masterCV', {}).get('title', 'My Master CV'))
    cv_content = st.text_area("📝 Paste Your CV Here", value=data.get('masterCV', {}).get('content', ''), height=200)
    
    if st.button("💾 Save CV", type="primary"):
        data['masterCV']['title'] = cv_title
        data['masterCV']['content'] = cv_content
        data['masterCV']['lastUpdated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = add_history(data, "Updated CV", "CV", cv_title)
        if save_data(data):
            st.success("✅ CV Saved Permanently!")
            time.sleep(0.5)
            st.rerun()

if data.get('masterCV', {}).get('content'):
    st.info(f"✅ CV saved: {data['masterCV'].get('lastUpdated', 'Never')}")

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
                if check_duplicate(data, 'scholarships', name):
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

# Display Scholarships with color coding
scholarships = data.get('scholarships', [])
if scholarships:
    st.subheader(f"📋 Your Scholarships ({len(scholarships)})")
    sorted_items = sorted(scholarships, key=lambda x: x.get('deadline', '9999-12-31'))
    
    for idx, s in enumerate(sorted_items):
        deadline_status = get_deadline_status(s.get('deadline'))
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{s.get('name', '')}**")
                if s.get('uni'): st.caption(f"🏛️ {s.get('uni')}")
                if s.get('country'): st.caption(f"🌍 {s.get('country')}")
                if s.get('notes'): st.caption(f"📝 {s.get('notes')[:100]}")
            with col2:
                st.write(f"📅 {s.get('deadline', 'No deadline')}")
                st.markdown(f"<span class='{deadline_status['class']}'>{deadline_status['label']}</span>", unsafe_allow_html=True)
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
                if check_duplicate(data, 'jobs', title):
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

# Display Jobs with color coding
jobs = data.get('jobs', [])
if jobs:
    st.subheader(f"📋 Your Jobs ({len(jobs)})")
    sorted_items = sorted(jobs, key=lambda x: x.get('deadline', '9999-12-31'))
    
    for idx, j in enumerate(sorted_items):
        deadline_status = get_deadline_status(j.get('deadline'))
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{j.get('title', '')}**")
                if j.get('company'): st.caption(f"🏢 {j.get('company')}")
                if j.get('location'): st.caption(f"📍 {j.get('location')}")
                if j.get('notes'): st.caption(f"📝 {j.get('notes')[:100]}")
            with col2:
                st.write(f"📅 {j.get('deadline', 'No deadline')}")
                st.markdown(f"<span class='{deadline_status['class']}'>{deadline_status['label']}</span>", unsafe_allow_html=True)
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

# ========== HISTORY LOG - FULL TEXT ==========

st.header("📜 Complete History Log - All Actions")

history = data.get('history', [])
if history:
    # Create full text version for copy
    history_text = "📜 COMPLETE HISTORY LOG\n"
    history_text += "=" * 50 + "\n"
    for h in reversed(history):
        history_text += f"{h.get('timestamp', '')} - {h.get('action', '')}: {h.get('name', '')}\n"
        if h.get('details'): history_text += f"  Details: {h.get('details')}\n"
    history_text += "=" * 50 + "\n"
    history_text += f"Total Actions: {len(history)}"
    
    st.text_area("📋 Full History (Copy this)", history_text, height=300)
    
    # Also show in nice format
    st.subheader("📋 History Timeline")
    for h in reversed(history):
        emoji = {"Added": "➕", "Submitted": "📤", "Accepted": "✅", "Rejected": "❌", "Deleted": "🗑️", "Updated CV": "📄"}.get(h.get('action', ''), "📌")
        st.markdown(f"""
        <div class="history-item">
            <b>{emoji} {h.get('action', '')}</b> {h.get('type', '')}: <b>{h.get('name', '')}</b>
            <br><small>🕐 {h.get('timestamp', '')}</small>
            {f'<br><small>📝 {h.get("details", "")}</small>' if h.get('details') else ''}
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No history yet. Start adding scholarships and jobs!")

# ========== FOOTER ==========

st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🇪🇹 Built for Ethiopian scholars")
with col2:
    st.caption("📦 Data saved permanently on GitHub")
with col3:
    st.caption(f"🔗 github.com/{USER}/{REPO}")

st.caption("✅ Zero-duplication | 🔒 Button lock | 📊 Live Dashboard | 💾 Permanent storage")
