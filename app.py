import streamlit as st
import requests
import json
import base64
from datetime import datetime, timedelta
import time
import pandas as pd
from calendar import monthcalendar, Calendar

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

# ========== PAGE CONFIG ==========

st.set_page_config(
    page_title="📚 Dagi Tracker Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========

st.markdown("""
<style>
    /* Welcome Section */
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
    
    /* 5S Dashboard */
    .ss-sort { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 15px; margin: 5px 0; text-align: center; }
    .ss-set { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 15px; border-radius: 15px; margin: 5px 0; text-align: center; }
    .ss-shine { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 15px; border-radius: 15px; margin: 5px 0; text-align: center; }
    .ss-standardize { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 15px; border-radius: 15px; margin: 5px 0; text-align: center; }
    .ss-sustain { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 15px; border-radius: 15px; margin: 5px 0; text-align: center; }
    
    /* Deadline Colors */
    .deadline-red { background: #dc3545; color: white; padding: 5px 15px; border-radius: 25px; font-weight: bold; display: inline-block; animation: blink 1s infinite; }
    .deadline-yellow { background: #ffc107; color: black; padding: 5px 15px; border-radius: 25px; font-weight: bold; display: inline-block; }
    .deadline-green { background: #28a745; color: white; padding: 5px 15px; border-radius: 25px; font-weight: bold; display: inline-block; }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* History Items */
    .history-item { 
        padding: 12px; 
        background: #f8f9fa; 
        border-radius: 10px; 
        margin: 5px 0;
        border-left: 5px solid #007bff;
        transition: all 0.3s;
    }
    .history-item:hover { background: #e9ecef; transform: translateX(5px); }
    
    /* Word Export Box */
    .word-export {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border: 3px solid #007bff;
        white-space: pre-wrap;
        font-family: 'Arial', sans-serif;
        min-height: 150px;
        max-height: 400px;
        overflow-y: auto;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Calendar Styling */
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
    
    .calendar-header {
        background: #007bff;
        color: white;
        padding: 10px;
        border-radius: 10px 10px 0 0;
        text-align: center;
        font-weight: bold;
    }
    
    /* Note Cards */
    .note-card {
        background: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 10px 0;
    }
    
    /* Individual Export Button */
    .export-btn {
        background: #28a745;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: bold;
    }
    .export-btn:hover { background: #218838; }
    
    /* Stats Cards */
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
</style>
""", unsafe_allow_html=True)

# ========== WELCOME SECTION ==========

current_time = datetime.now()
day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_name = day_names[current_time.weekday()]

st.markdown(f"""
<div class="welcome-box">
    <div class="welcome-title">👋 Welcome, Dagim!</div>
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
        "date": datetime.now().strftime("%Y-%m-%d"),
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

def generate_individual_word(item, item_type):
    """Generate Word document for a single item"""
    word = "=" * 60 + "\n"
    word += f"📚 {item_type.upper()} DETAILS\n"
    word += "=" * 60 + "\n\n"
    
    if item_type == "scholarship":
        word += f"🎓 Name: {item.get('name', 'N/A')}\n"
        word += f"🏛️ University: {item.get('uni', 'N/A')}\n"
        word += f"📅 Deadline: {item.get('deadline', 'N/A')}\n"
        word += f"🌍 Country: {item.get('country', 'N/A')}\n"
        word += f"📊 Status: {item.get('status', 'active')}\n"
        word += f"📝 Notes: {item.get('notes', 'N/A')}\n"
        word += f"🔗 Link: {item.get('link', 'N/A')}\n"
        word += f"🕐 Added: {item.get('createdAt', 'N/A')}\n"
    else:  # job
        word += f"💼 Title: {item.get('title', 'N/A')}\n"
        word += f"🏢 Company: {item.get('company', 'N/A')}\n"
        word += f"📅 Deadline: {item.get('deadline', 'N/A')}\n"
        word += f"📍 Location: {item.get('location', 'N/A')}\n"
        word += f"📊 Status: {item.get('status', 'active')}\n"
        word += f"📝 Notes: {item.get('notes', 'N/A')}\n"
        word += f"🔗 Link: {item.get('link', 'N/A')}\n"
        word += f"🕐 Added: {item.get('createdAt', 'N/A')}\n"
    
    word += "\n" + "=" * 60 + "\n"
    word += f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    word += "=" * 60 + "\n"
    
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
    total_s = len(data.get('scholarships', []))
    total_j = len(data.get('jobs', []))
    st.metric("🎓 Scholarships", total_s)
    st.metric("💼 Jobs", total_j)
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
            <div class="stats-label">✅ Completion</div>
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
    
    st.progress(completion / 100)
    st.caption(f"📈 Progress: {completion}% complete")

st.markdown("---")

# ========== MASTER CV SECTION ==========

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
    with st.expander("👁️ View CV"):
        st.text(data['masterCV'].get('content', ''))

st.markdown("---")

# ========== CALENDAR & DATE FILTER ==========

st.header("📅 Calendar - Click a Date to Filter History")

current_date = datetime.now()
current_month = current_date.month
current_year = current_date.year

# Month navigation
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

# Get calendar for month
cal = monthcalendar(current_year, current_month)

# Build calendar grid
days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
cols = st.columns(7)

for i, day in enumerate(days_of_week):
    cols[i].markdown(f"<div style='text-align: center; font-weight: bold;'>{day}</div>", unsafe_allow_html=True)

# Get dates with history
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
            
            # Determine style
            style = "calendar-day"
            if is_today: style += " today"
            if has_items: style += " has-items"
            if is_selected: style += " selected"
            
            # Create button for each day
            if cols[i].button(str(day), key=f"cal_{date_str}", use_container_width=True):
                st.session_state.selected_date = date_str if st.session_state.selected_date != date_str else None
                st.rerun()

# Show selected date items
if st.session_state.selected_date:
    selected_date = st.session_state.selected_date
    st.subheader(f"📋 History for {selected_date}")
    
    filtered_history = [h for h in data.get('history', []) if h.get('date', '') == selected_date]
    
    if filtered_history:
        for h in filtered_history:
            emoji = {"Added": "➕", "Submitted": "📤", "Accepted": "✅", "Rejected": "❌", "Deleted": "🗑️", "Updated CV": "📄"}.get(h.get('action', ''), "📌")
            st.markdown(f"""
            <div class="history-item">
                <b>{emoji} {h.get('action', '')}</b> {h.get('type', '')}: <b>{h.get('name', '')}</b>
                <br><small>🕐 {h.get('timestamp', '')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No history for this date")
    
    if st.button("Clear Filter"):
        st.session_state.selected_date = None
        st.rerun()

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

# Display Scholarships with INDIVIDUAL EXPORT
scholarships = data.get('scholarships', [])
if scholarships:
    st.subheader(f"📋 Your Scholarships ({len(scholarships)})")
    sorted_items = sorted(scholarships, key=lambda x: x.get('deadline', '9999-12-31'))
    
    for idx, s in enumerate(sorted_items):
        deadline_status = get_deadline_status(s.get('deadline'))
        with st.container():
            col1, col2, col3, col4 = st.columns([2.5, 1.5, 1, 1])
            with col1:
                st.markdown(f"**{s.get('name', '')}**")
                if s.get('uni'): st.caption(f"🏛️ {s.get('uni')}")
                if s.get('country'): st.caption(f"🌍 {s.get('country')}")
                if s.get('notes'): st.caption(f"📝 {s.get('notes')[:80]}")
            with col2:
                st.write(f"📅 {s.get('deadline', 'No deadline')}")
                st.markdown(f"<span class='{deadline_status['class']}'>{deadline_status['label']}</span>", unsafe_allow_html=True)
                status = s.get('status', 'active')
                icons = {"active": "🟢 Active", "submitted": "📤 Submitted", "accepted": "✅ Accepted", "rejected": "❌ Rejected"}
                st.write(icons.get(status, status))
            with col3:
                # Individual Word Export Button
                if st.button("📄 Export Word", key=f"s_export_{idx}"):
                    word_content = generate_individual_word(s, "scholarship")
                    st.session_state[f"word_export_s_{idx}"] = word_content
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
            
            # Show individual export if exists
            if st.session_state.get(f"word_export_s_{idx}"):
                st.markdown(f"""
                <div class="word-export">
                    {st.session_state[f"word_export_s_{idx}"]}
                </div>
                """, unsafe_allow_html=True)
                if st.button("📋 Copy to Clipboard", key=f"s_copy_{idx}"):
                    st.info("✅ Select text above and press Ctrl+C")
            
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

# Display Jobs with INDIVIDUAL EXPORT
jobs = data.get('jobs', [])
if jobs:
    st.subheader(f"📋 Your Jobs ({len(jobs)})")
    sorted_items = sorted(jobs, key=lambda x: x.get('deadline', '9999-12-31'))
    
    for idx, j in enumerate(sorted_items):
        deadline_status = get_deadline_status(j.get('deadline'))
        with st.container():
            col1, col2, col3, col4 = st.columns([2.5, 1.5, 1, 1])
            with col1:
                st.markdown(f"**{j.get('title', '')}**")
                if j.get('company'): st.caption(f"🏢 {j.get('company')}")
                if j.get('location'): st.caption(f"📍 {j.get('location')}")
                if j.get('notes'): st.caption(f"📝 {j.get('notes')[:80]}")
            with col2:
                st.write(f"📅 {j.get('deadline', 'No deadline')}")
                st.markdown(f"<span class='{deadline_status['class']}'>{deadline_status['label']}</span>", unsafe_allow_html=True)
                status = j.get('status', 'active')
                icons = {"active": "🟢 Active", "submitted": "📤 Submitted", "accepted": "✅ Accepted", "rejected": "❌ Rejected"}
                st.write(icons.get(status, status))
            with col3:
                # Individual Word Export Button
                if st.button("📄 Export Word", key=f"j_export_{idx}"):
                    word_content = generate_individual_word(j, "job")
                    st.session_state[f"word_export_j_{idx}"] = word_content
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
            
            # Show individual export if exists
            if st.session_state.get(f"word_export_j_{idx}"):
                st.markdown(f"""
                <div class="word-export">
                    {st.session_state[f"word_export_j_{idx}"]}
                </div>
                """, unsafe_allow_html=True)
                if st.button("📋 Copy to Clipboard", key=f"j_copy_{idx}"):
                    st.info("✅ Select text above and press Ctrl+C")
            
            st.divider()

st.markdown("---")

# ========== NOTES SECTION ==========

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

# ========== COMPLETE HISTORY ==========

st.header("📜 Complete History Log")

# Full history export
if data.get('history'):
    full_history = "📜 COMPLETE HISTORY\n"
    full_history += "=" * 60 + "\n"
    for h in reversed(data['history']):
        full_history += f"{h.get('timestamp', '')} - {h.get('action', '')}: {h.get('name', '')}\n"
        if h.get('details'): full_history += f"  Details: {h.get('details')}\n"
    full_history += "=" * 60 + "\n"
    full_history += f"Total: {len(data['history'])} actions"
    
    if st.button("📄 Export Full History as Word"):
        st.session_state.full_history_export = full_history
        st.rerun()
    
    if st.session_state.get('full_history_export'):
        st.markdown(f"""
        <div class="word-export">
            {st.session_state.full_history_export}
        </div>
        """, unsafe_allow_html=True)
        if st.button("📋 Copy Full History"):
            st.info("✅ Select text above and press Ctrl+C")
    
    st.subheader("📋 History Timeline")
    for h in reversed(data['history']):
        emoji = {"Added": "➕", "Submitted": "📤", "Accepted": "✅", "Rejected": "❌", "Deleted": "🗑️", "Updated CV": "📄"}.get(h.get('action', ''), "📌")
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

st.caption("✅ Zero-duplication | 🔒 Button lock | 📊 Live Dashboard | 💾 Permanent storage")
