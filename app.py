import streamlit as st
import requests
import json
import base64
from datetime import datetime, timedelta
import time

# ========== GET TOKEN FROM STREAMLIT SECRETS ==========

try:
    TOKEN = st.secrets["TOKEN"]
except:
    TOKEN = None

# Your GitHub info
USER = "digitalirrigation-lgtm"
REPO = "dagi"
FILE = "data.json"

# Check if token works
if not TOKEN:
    st.error("❌ No token found! Add TOKEN to Streamlit secrets.")
    st.stop()

st.set_page_config(page_title="📚 Dagi Tracker Pro", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    .success-box {
        padding: 10px;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        border-radius: 5px;
        margin: 5px 0;
    }
    .warning-box {
        padding: 10px;
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        border-radius: 5px;
        margin: 5px 0;
    }
    .danger-box {
        padding: 10px;
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        border-radius: 5px;
        margin: 5px 0;
    }
    .info-box {
        padding: 10px;
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        border-radius: 5px;
        margin: 5px 0;
    }
    .history-item {
        padding: 8px;
        background-color: #f8f9fa;
        border-radius: 5px;
        margin: 3px 0;
        font-size: 0.9em;
    }
    .deadline-urgent {
        background-color: #dc3545;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
    }
    .deadline-soon {
        background-color: #ffc107;
        color: black;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
    }
    .deadline-safe {
        background-color: #28a745;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 My Scholarship & Job Tracker Pro")
st.caption("🔒 Zero-duplication | 💾 Permanent storage | 📊 Smart tracking")

# ========== GITHUB FUNCTIONS ==========

def get_data():
    """Fetch data from GitHub"""
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
    headers = {
        'Authorization': f'token {TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            content = response.json()['content']
            decoded = base64.b64decode(content).decode('utf-8')
            data = json.loads(decoded)
            
            # Make sure all fields exist
            if 'scholarships' not in data:
                data['scholarships'] = []
            if 'jobs' not in data:
                data['jobs'] = []
            if 'masterCV' not in data:
                data['masterCV'] = {"title": "My Master CV", "content": "", "lastUpdated": ""}
            if 'history' not in data:
                data['history'] = []
            
            return data
        else:
            # Create default data
            default_data = {
                "scholarships": [],
                "jobs": [],
                "masterCV": {
                    "title": "My Master CV",
                    "content": "",
                    "lastUpdated": ""
                },
                "history": []
            }
            save_data(default_data)
            return default_data
            
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return {
            "scholarships": [],
            "jobs": [],
            "masterCV": {
                "title": "My Master CV",
                "content": "",
                "lastUpdated": ""
            },
            "history": []
        }

def save_data(data):
    """Save data to GitHub with proper error handling"""
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
    headers = {
        'Authorization': f'token {TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Get current file SHA first
        sha = None
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                sha = response.json()['sha']
        except:
            pass
        
        # Prepare content
        content = base64.b64encode(
            json.dumps(data, indent=2, default=str).encode('utf-8')
        ).decode('utf-8')
        
        payload = {
            'message': f'Update data - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'content': content,
            'branch': 'main'
        }
        
        if sha:
            payload['sha'] = sha
        
        # Save to GitHub
        response = requests.put(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code in [200, 201]:
            return True
        else:
            return False
            
    except Exception as e:
        return False

def add_history(data, action, item_type, item_name, details=""):
    """Add entry to history log"""
    if 'history' not in data:
        data['history'] = []
    
    history_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "type": item_type,
        "name": item_name,
        "details": details
    }
    data['history'].append(history_entry)
    return data

def check_duplicate(data, item_type, name):
    """Check if item already exists (case-insensitive)"""
    items = data.get(item_type, [])
    for item in items:
        if item.get('name', '').lower() == name.lower():
            return True
    return False

def get_deadline_status(deadline_str):
    """Get deadline status with color coding"""
    if not deadline_str:
        return {"label": "No deadline", "class": "deadline-safe"}
    
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        days_left = (deadline - datetime.now()).days
        
        if days_left < 0:
            return {"label": f"⏰ EXPIRED ({abs(days_left)} days ago)", "class": "deadline-urgent"}
        elif days_left <= 3:
            return {"label": f"🔴 URGENT! {days_left} days left", "class": "deadline-urgent"}
        elif days_left <= 7:
            return {"label": f"🟡 {days_left} days left", "class": "deadline-soon"}
        else:
            return {"label": f"🟢 {days_left} days left", "class": "deadline-safe"}
    except:
        return {"label": "Invalid date", "class": "deadline-safe"}

# ========== LOAD DATA ==========

if 'data' not in st.session_state:
    st.session_state.data = get_data()
    st.session_state.save_clicked = False

data = st.session_state.data

# ========== SIDEBAR ==========

with st.sidebar:
    st.success("✅ Connected to GitHub!")
    st.write(f"📁 Repository: {REPO}")
    
    st.markdown("---")
    
    st.subheader("📊 Stats")
    total_scholarships = len(data.get('scholarships', []))
    total_jobs = len(data.get('jobs', []))
    st.write(f"🎓 Scholarships: {total_scholarships}")
    st.write(f"💼 Jobs: {total_jobs}")
    
    # Count by status
    active = len([s for s in data.get('scholarships', []) if s.get('status') == 'active']) + \
             len([j for j in data.get('jobs', []) if j.get('status') == 'active'])
    submitted = len([s for s in data.get('scholarships', []) if s.get('status') == 'submitted']) + \
                len([j for j in data.get('jobs', []) if j.get('status') == 'submitted'])
    accepted = len([s for s in data.get('scholarships', []) if s.get('status') == 'accepted']) + \
               len([j for j in data.get('jobs', []) if j.get('status') == 'accepted'])
    
    st.write(f"🟢 Active: {active}")
    st.write(f"📤 Submitted: {submitted}")
    st.write(f"✅ Accepted: {accepted}")
    
    st.markdown("---")
    
    st.subheader("📜 Recent History")
    history = data.get('history', [])
    if history:
        for h in history[-5:]:  # Show last 5
            st.markdown(f"""
            <div class="history-item">
                <small>{h.get('timestamp', '')}</small><br>
                <b>{h.get('action', '')}</b> {h.get('name', '')}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No history yet")
    
    st.markdown("---")
    st.caption("📦 Data saved on GitHub")
    st.caption(f"🔗 github.com/{USER}/{REPO}")

# ========== MASTER CV ==========

st.header("📄 Master CV")

with st.expander("✏️ Edit Your Master CV", expanded=False):
    cv_title = st.text_input("CV Title", value=data.get('masterCV', {}).get('title', 'My Master CV'))
    cv_content = st.text_area("📝 Paste Your CV", value=data.get('masterCV', {}).get('content', ''), height=150)
    
    if st.button("💾 Save CV", type="primary"):
        data['masterCV']['title'] = cv_title
        data['masterCV']['content'] = cv_content
        data['masterCV']['lastUpdated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = add_history(data, "Updated CV", "CV", cv_title)
        if save_data(data):
            st.success("✅ CV Saved!")
            st.rerun()

# Show saved CV
if data.get('masterCV', {}).get('content'):
    st.info(f"✅ CV saved: {data['masterCV'].get('lastUpdated', 'Never')}")

# ========== SCHOLARSHIPS ==========

st.header("🎓 Scholarships")

# Add Scholarship
with st.expander("➕ Add New Scholarship", expanded=False):
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
            if check_duplicate(data, 'scholarships', name):
                st.error(f"❌ DUPLICATE! '{name}' already exists! No duplicate allowed!")
            else:
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
                data = add_history(data, "Added", "Scholarship", name, f"Deadline: {deadline.strftime('%Y-%m-%d')}")
                if save_data(data):
                    st.success(f"✅ '{name}' Saved Permanently!")
                    time.sleep(0.5)
                    st.rerun()
        else:
            st.error("❌ Name and Deadline are required!")

# Display Scholarships
scholarships = data.get('scholarships', [])
if scholarships:
    st.subheader(f"📋 Your Scholarships ({len(scholarships)})")
    
    # Sort by deadline (closest first)
    sorted_items = sorted(scholarships, key=lambda x: x.get('deadline', '9999-12-31'))
    
    for idx, s in enumerate(sorted_items):
        deadline_status = get_deadline_status(s.get('deadline'))
        
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{s.get('name', '')}**")
                if s.get('uni'):
                    st.caption(f"🏛️ {s.get('uni')}")
                if s.get('country'):
                    st.caption(f"🌍 {s.get('country')}")
                if s.get('notes'):
                    st.caption(f"📝 {s.get('notes')[:100]}")
                if s.get('link'):
                    st.caption(f"🔗 [Link]({s.get('link')})")
            with col2:
                st.write(f"📅 {s.get('deadline', 'No deadline')}")
                st.markdown(f"<span class='{deadline_status['class']}'>{deadline_status['label']}</span>", unsafe_allow_html=True)
                status = s.get('status', 'active')
                if status == 'active':
                    st.write("🟢 Active")
                elif status == 'submitted':
                    st.write("📤 Submitted")
                elif status == 'accepted':
                    st.write("✅ Accepted")
                elif status == 'rejected':
                    st.write("❌ Rejected")
            with col3:
                if s.get('status') == 'active':
                    if st.button("📤 Submit", key=f"s_sub_{idx}"):
                        s['status'] = 'submitted'
                        data = add_history(data, "Submitted", "Scholarship", s.get('name'))
                        save_data(data)
                        st.rerun()
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
            st.divider()
else:
    st.info("No scholarships yet. Add your first one above!")

# ========== JOBS ==========

st.header("💼 Jobs")

# Add Job
with st.expander("➕ Add New Job", expanded=False):
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
            # Check for duplicates
            if check_duplicate(data, 'jobs', title):
                st.error(f"❌ DUPLICATE! '{title}' already exists! No duplicate allowed!")
            else:
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
                data = add_history(data, "Added", "Job", title, f"Company: {company}")
                if save_data(data):
                    st.success(f"✅ '{title}' Saved Permanently!")
                    time.sleep(0.5)
                    st.rerun()
        else:
            st.error("❌ Title, Company, and Deadline are required!")

# Display Jobs
jobs = data.get('jobs', [])
if jobs:
    st.subheader(f"📋 Your Jobs ({len(jobs)})")
    
    # Sort by deadline (closest first)
    sorted_items = sorted(jobs, key=lambda x: x.get('deadline', '9999-12-31'))
    
    for idx, j in enumerate(sorted_items):
        deadline_status = get_deadline_status(j.get('deadline'))
        
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{j.get('title', '')}**")
                if j.get('company'):
                    st.caption(f"🏢 {j.get('company')}")
                if j.get('location'):
                    st.caption(f"📍 {j.get('location')}")
                if j.get('notes'):
                    st.caption(f"📝 {j.get('notes')[:100]}")
                if j.get('link'):
                    st.caption(f"🔗 [Link]({j.get('link')})")
            with col2:
                st.write(f"📅 {j.get('deadline', 'No deadline')}")
                st.markdown(f"<span class='{deadline_status['class']}'>{deadline_status['label']}</span>", unsafe_allow_html=True)
                status = j.get('status', 'active')
                if status == 'active':
                    st.write("🟢 Active")
                elif status == 'submitted':
                    st.write("📤 Submitted")
                elif status == 'accepted':
                    st.write("✅ Accepted")
                elif status == 'rejected':
                    st.write("❌ Rejected")
            with col3:
                if j.get('status') == 'active':
                    if st.button("📤 Submit", key=f"j_sub_{idx}"):
                        j['status'] = 'submitted'
                        data = add_history(data, "Submitted", "Job", j.get('title'))
                        save_data(data)
                        st.rerun()
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
            st.divider()
else:
    st.info("No jobs yet. Add your first one above!")

# ========== HISTORY TAB ==========

st.header("📜 Complete History Log")

history = data.get('history', [])
if history:
    # Reverse to show newest first
    for h in reversed(history):
        timestamp = h.get('timestamp', '')
        action = h.get('action', '')
        item_type = h.get('type', '')
        name = h.get('name', '')
        details = h.get('details', '')
        
        emoji = {
            "Added": "➕",
            "Submitted": "📤",
            "Accepted": "✅",
            "Rejected": "❌",
            "Deleted": "🗑️",
            "Updated CV": "📄"
        }.get(action, "📌")
        
        st.markdown(f"""
        <div class="history-item">
            <b>{emoji} {action}</b> {item_type}: <b>{name}</b>
            <br><small>🕐 {timestamp}</small>
            {f'<br><small>📝 {details}</small>' if details else ''}
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No history yet. Start adding scholarships and jobs!")

# ========== FOOTER ==========

st.markdown("---")
st.caption("🇪🇹 Built for Ethiopian scholars | Zero-duplication | Permanent GitHub storage")
st.caption(f"📦 https://github.com/{USER}/{REPO}")
