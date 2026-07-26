import streamlit as st
import requests
import json
import base64
from datetime import datetime, timedelta
import time
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

st.set_page_config(
    page_title="📚 Dagi Tracker Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========

st.markdown("""
<style>
    /* 5S Colors */
    .ss-sort { background: #4CAF50; color: white; padding: 10px; border-radius: 10px; margin: 5px 0; }
    .ss-set { background: #2196F3; color: white; padding: 10px; border-radius: 10px; margin: 5px 0; }
    .ss-shine { background: #FF9800; color: white; padding: 10px; border-radius: 10px; margin: 5px 0; }
    .ss-standardize { background: #9C27B0; color: white; padding: 10px; border-radius: 10px; margin: 5px 0; }
    .ss-sustain { background: #f44336; color: white; padding: 10px; border-radius: 10px; margin: 5px 0; }
    
    .deadline-red { background: #dc3545; color: white; padding: 3px 12px; border-radius: 20px; font-weight: bold; }
    .deadline-yellow { background: #ffc107; color: black; padding: 3px 12px; border-radius: 20px; font-weight: bold; }
    .deadline-green { background: #28a745; color: white; padding: 3px 12px; border-radius: 20px; font-weight: bold; }
    
    .history-item { 
        padding: 10px; 
        background: #f8f9fa; 
        border-radius: 8px; 
        margin: 5px 0;
        border-left: 4px solid #007bff;
    }
    
    .word-export {
        background: #f0f0f0;
        padding: 20px;
        border-radius: 10px;
        border: 2px dashed #007bff;
        white-space: pre-wrap;
        font-family: 'Arial', sans-serif;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
    }
    
    .button-locked {
        opacity: 0.5;
        pointer-events: none;
    }
    
    /* Progress bar animation */
    @keyframes progress {
        from { width: 0%; }
        to { width: 100%; }
    }
</style>
""", unsafe_allow_html=True)

st.title("📚 My Scholarship & Job Tracker Pro")
st.caption("🔒 5S Methodology | 💾 Permanent GitHub Storage | 📊 Real-time Progress")

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
            if 'wordExport' not in data:
                data['wordExport'] = []
            
            return data
        else:
            default_data = {
                "scholarships": [],
                "jobs": [],
                "masterCV": {"title": "My Master CV", "content": "", "lastUpdated": ""},
                "history": [],
                "wordExport": []
            }
            save_data(default_data)
            return default_data
            
    except Exception as e:
        return {
            "scholarships": [],
            "jobs": [],
            "masterCV": {"title": "My Master CV", "content": "", "lastUpdated": ""},
            "history": [],
            "wordExport": []
        }

def save_data(data):
    """Save data to GitHub"""
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
    headers = {
        'Authorization': f'token {TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        sha = None
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                sha = response.json()['sha']
        except:
            pass
        
        content = base64.b64encode(
            json.dumps(data, indent=2, default=str).encode('utf-8')
        ).decode('utf-8')
        
        payload = {
            'message': f'Update - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'content': content,
            'branch': 'main'
        }
        
        if sha:
            payload['sha'] = sha
        
        response = requests.put(url, headers=headers, json=payload, timeout=10)
        return response.status_code in [200, 201]
            
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

def add_word_export(data, text):
    """Add to word export history"""
    if 'wordExport' not in data:
        data['wordExport'] = []
    
    word_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content": text
    }
    data['wordExport'].append(word_entry)
    return data

def check_duplicate(data, item_type, name):
    """Check if item already exists"""
    items = data.get(item_type, [])
    for item in items:
        if item.get('name', '').lower() == name.lower():
            return True
    return False

def get_deadline_status(deadline_str):
    """Get deadline status with color coding"""
    if not deadline_str:
        return {"label": "No deadline", "class": "deadline-green"}
    
    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        days_left = (deadline - datetime.now()).days
        
        if days_left < 0:
            return {"label": f"⏰ EXPIRED ({abs(days_left)} days ago)", "class": "deadline-red"}
        elif days_left <= 5:
            return {"label": f"🔴 {days_left} days left", "class": "deadline-red"}
        elif days_left <= 20:
            return {"label": f"🟡 {days_left} days left", "class": "deadline-yellow"}
        else:
            return {"label": f"🟢 {days_left} days left", "class": "deadline-green"}
    except:
        return {"label": "Invalid date", "class": "deadline-green"}

# ========== LOAD DATA ==========

if 'data' not in st.session_state:
    st.session_state.data = get_data()
    st.session_state.save_clicked = False

data = st.session_state.data

# ========== 5S DASHBOARD ==========

st.header("🏭 5S Dashboard - Status")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div class="ss-sort">
        <b>📋 SORT</b><br>
        <small>Keep only essentials</small><br>
        <b>Active: {}</b>
    </div>
    """.format(len([s for s in data.get('scholarships', []) if s.get('status') == 'active']) +
               len([j for j in data.get('jobs', []) if j.get('status') == 'active'])), 
    unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="ss-set">
        <b>📌 SET</b><br>
        <small>Organized tracking</small><br>
        <b>Total: {}</b>
    </div>
    """.format(len(data.get('scholarships', [])) + len(data.get('jobs', []))), 
    unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="ss-shine">
        <b>✨ SHINE</b><br>
        <small>Clean & updated</small><br>
        <b>Submitted: {}</b>
    </div>
    """.format(len([s for s in data.get('scholarships', []) if s.get('status') == 'submitted']) +
               len([j for j in data.get('jobs', []) if j.get('status') == 'submitted'])), 
    unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="ss-standardize">
        <b>📏 STANDARDIZE</b><br>
        <small>Consistent process</small><br>
        <b>Accepted: {}</b>
    </div>
    """.format(len([s for s in data.get('scholarships', []) if s.get('status') == 'accepted']) +
               len([j for j in data.get('jobs', []) if j.get('status') == 'accepted'])), 
    unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="ss-sustain">
        <b>♻️ SUSTAIN</b><br>
        <small>Continuous progress</small><br>
        <b>History: {}</b>
    </div>
    """.format(len(data.get('history', []))), 
    unsafe_allow_html=True)

st.markdown("---")

# ========== SIDEBAR ==========

with st.sidebar:
    st.success("✅ Connected to GitHub!")
    st.write(f"📁 Repository: {REPO}")
    
    st.markdown("---")
    
    st.subheader("📊 Quick Stats")
    total_scholarships = len(data.get('scholarships', []))
    total_jobs = len(data.get('jobs', []))
    st.metric("🎓 Scholarships", total_scholarships)
    st.metric("💼 Jobs", total_jobs)
    
    st.markdown("---")
    
    st.subheader("📜 Recent History")
    history = data.get('history', [])
    if history:
        for h in history[-3:]:
            st.markdown(f"""
            <div class="history-item">
                <small>{h.get('timestamp', '')}</small><br>
                <b>{h.get('action', '')}</b> {h.get('name', '')}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("📦 Data saved on GitHub")
    st.caption(f"🔗 github.com/{USER}/{REPO}")

# ========== WORD FORMAT EXPORT ==========

st.header("📄 Word Format Export")

if st.button("📝 Generate Word Format Report", type="primary"):
    word_content = "========================================\n"
    word_content += "📚 SCHOLARSHIP & JOB TRACKER REPORT\n"
    word_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    word_content += "========================================\n\n"
    
    word_content += "🎓 SCHOLARSHIPS\n"
    word_content += "-" * 40 + "\n"
    for s in data.get('scholarships', []):
        word_content += f"• {s.get('name', '')}\n"
        word_content += f"  University: {s.get('uni', 'N/A')}\n"
        word_content += f"  Deadline: {s.get('deadline', 'N/A')}\n"
        word_content += f"  Status: {s.get('status', 'active')}\n"
        if s.get('notes'):
            word_content += f"  Notes: {s.get('notes')}\n"
        word_content += "\n"
    
    word_content += "\n💼 JOBS\n"
    word_content += "-" * 40 + "\n"
    for j in data.get('jobs', []):
        word_content += f"• {j.get('title', '')}\n"
        word_content += f"  Company: {j.get('company', 'N/A')}\n"
        word_content += f"  Deadline: {j.get('deadline', 'N/A')}\n"
        word_content += f"  Status: {j.get('status', 'active')}\n"
        if j.get('notes'):
            word_content += f"  Notes: {j.get('notes')}\n"
        word_content += "\n"
    
    word_content += "📜 HISTORY LOG\n"
    word_content += "-" * 40 + "\n"
    for h in data.get('history', []):
        word_content += f"{h.get('timestamp', '')} - {h.get('action', '')}: {h.get('name', '')}\n"
    
    word_content += "\n========================================\n"
    word_content += "📊 SUMMARY STATISTICS\n"
    word_content += "========================================\n"
    word_content += f"Total Scholarships: {len(data.get('scholarships', []))}\n"
    word_content += f"Total Jobs: {len(data.get('jobs', []))}\n"
    word_content += f"Total Actions: {len(data.get('history', []))}\n"
    word_content += f"Active: {len([s for s in data.get('scholarships', []) if s.get('status') == 'active']) + len([j for j in data.get('jobs', []) if j.get('status') == 'active'])}\n"
    word_content += f"Submitted: {len([s for s in data.get('scholarships', []) if s.get('status') == 'submitted']) + len([j for j in data.get('jobs', []) if j.get('status') == 'submitted'])}\n"
    word_content += f"Accepted: {len([s for s in data.get('scholarships', []) if s.get('status') == 'accepted']) + len([j for j in data.get('jobs', []) if j.get('status') == 'accepted'])}\n"
    
    data = add_word_export(data, word_content)
    save_data(data)
    
    st.session_state.word_content = word_content
    st.rerun()

if 'word_content' in st.session_state:
    st.markdown(f"""
    <div class="word-export">
        {st.session_state.word_content}
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📋 Copy to Clipboard"):
        st.write("✅ Ready to copy! Select all text above and press Ctrl+C")

# ========== MASTER CV ==========

st.header("📄 Master CV")

with st.expander("✏️ Edit Your Master CV", expanded=False):
    cv_title = st.text_input("CV Title", value=data.get('masterCV', {}).get('title', 'My Master CV'))
    cv_content = st.text_area("📝 Paste Your CV", value=data.get('masterCV', {}).get('content', ''), height=200)
    
    if st.button("💾 Save CV", type="primary"):
        data['masterCV']['title'] = cv_title
        data['masterCV']['content'] = cv_content
        data['masterCV']['lastUpdated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = add_history(data, "Updated CV", "CV", cv_title)
        if save_data(data):
            st.success("✅ CV Saved Permanently!")
            time.sleep(0.5)
            st.rerun()

# ========== SCHOLARSHIPS ==========

st.header("🎓 Scholarships")

# Add Scholarship with button lock
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
                        st.success(f"✅ '{name}' Saved!")
                        time.sleep(0.5)
                        st.session_state.s_saving = False
                        st.rerun()
            else:
                st.error("❌ Name and Deadline are required!")
    else:
        st.info("⏳ Saving... Please wait 2 seconds")
        time.sleep(2)
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
                if s.get('uni'):
                    st.caption(f"🏛️ {s.get('uni')}")
                if s.get('country'):
                    st.caption(f"🌍 {s.get('country')}")
                if s.get('notes'):
                    st.caption(f"📝 {s.get('notes')[:100]}")
            with col2:
                st.write(f"📅 {s.get('deadline', 'No deadline')}")
                st.markdown(f"<span class='{deadline_status['class']}'>{deadline_status['label']}</span>", unsafe_allow_html=True)
                status = s.get('status', 'active')
                status_icons = {"active": "🟢 Active", "submitted": "📤 Submitted", "accepted": "✅ Accepted", "rejected": "❌ Rejected"}
                st.write(status_icons.get(status, status))
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

# ========== JOBS ==========

st.header("💼 Jobs")

# Add Job with button lock
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
                        st.success(f"✅ '{title}' Saved!")
                        time.sleep(0.5)
                        st.session_state.j_saving = False
                        st.rerun()
            else:
                st.error("❌ Title, Company, and Deadline are required!")
    else:
        st.info("⏳ Saving... Please wait 2 seconds")
        time.sleep(2)
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
                if j.get('company'):
                    st.caption(f"🏢 {j.get('company')}")
                if j.get('location'):
                    st.caption(f"📍 {j.get('location')}")
                if j.get('notes'):
                    st.caption(f"📝 {j.get('notes')[:100]}")
            with col2:
                st.write(f"📅 {j.get('deadline', 'No deadline')}")
                st.markdown(f"<span class='{deadline_status['class']}'>{deadline_status['label']}</span>", unsafe_allow_html=True)
                status = j.get('status', 'active')
                status_icons = {"active": "🟢 Active", "submitted": "📤 Submitted", "accepted": "✅ Accepted", "rejected": "❌ Rejected"}
                st.write(status_icons.get(status, status))
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

# ========== PROGRESS GRAPH ==========

st.header("📈 Continuous Progress Graph")

if data.get('scholarships') or data.get('jobs'):
    # Prepare data for graph
    all_items = []
    
    for s in data.get('scholarships', []):
        days_left = 0
        try:
            deadline = datetime.strptime(s.get('deadline', ''), '%Y-%m-%d')
            days_left = (deadline - datetime.now()).days
        except:
            pass
        
        all_items.append({
            'name': s.get('name', 'Unknown'),
            'type': 'Scholarship',
            'deadline': s.get('deadline', ''),
            'days_left': days_left,
            'status': s.get('status', 'active')
        })
    
    for j in data.get('jobs', []):
        days_left = 0
        try:
            deadline = datetime.strptime(j.get('deadline', ''), '%Y-%m-%d')
            days_left = (deadline - datetime.now()).days
        except:
            pass
        
        all_items.append({
            'name': j.get('title', 'Unknown'),
            'type': 'Job',
            'deadline': j.get('deadline', ''),
            'days_left': days_left,
            'status': j.get('status', 'active')
        })
    
    if all_items:
        df = pd.DataFrame(all_items)
        df = df.sort_values('days_left')
        
        fig = make_subplots(rows=2, cols=1, 
                            subplot_titles=('📊 Progress Over Time', '📈 Distribution by Status'),
                            vertical_spacing=0.2)
        
        # Line graph for progress
        colors = {'active': '#4CAF50', 'submitted': '#FF9800', 'accepted': '#2196F3', 'rejected': '#f44336'}
        df['color'] = df['status'].map(colors)
        
        fig.add_trace(
            go.Scatter(
                x=df['name'],
                y=df['days_left'],
                mode='lines+markers+text',
                name='Days Left',
                text=df['days_left'],
                textposition='top center',
                marker=dict(size=12, color=df['color']),
                line=dict(color='#667eea', width=3)
            ),
            row=1, col=1
        )
        
        # Histogram
        status_counts = df['status'].value_counts()
        fig.add_trace(
            go.Bar(
                x=status_counts.index,
                y=status_counts.values,
                name='Status Count',
                marker=dict(color=['#4CAF50', '#FF9800', '#2196F3', '#f44336'])
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        fig.update_xaxes(title_text="Items", row=1, col=1)
        fig.update_yaxes(title_text="Days Left", row=1, col=1)
        fig.update_xaxes(title_text="Status", row=2, col=1)
        fig.update_yaxes(title_text="Count", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)

# ========== HISTORY LOG ==========

st.header("📜 Complete History Log")

history = data.get('history', [])
if history:
    # Show only history entries (no word exports)
    history_only = [h for h in history if not h.get('action', '').startswith('Word')]
    
    if history_only:
        for h in reversed(history_only[-20:]):  # Show last 20
            emoji = {
                "Added": "➕",
                "Submitted": "📤",
                "Accepted": "✅",
                "Rejected": "❌",
                "Deleted": "🗑️",
                "Updated CV": "📄"
            }.get(h.get('action', ''), "📌")
            
            st.markdown(f"""
            <div class="history-item">
                <b>{emoji} {h.get('action', '')}</b> {h.get('type', '')}: <b>{h.get('name', '')}</b>
                <br><small>🕐 {h.get('timestamp', '')}</small>
                {f'<br><small>📝 {h.get("details", "")}</small>' if h.get('details') else ''}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No history yet")
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

st.caption("✅ Zero-duplication | 🔒 Button lock | 📊 5S Dashboard | 💾 Permanent storage")
