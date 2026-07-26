import streamlit as st
import requests
import json
import base64
from datetime import datetime
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

st.set_page_config(page_title="📚 Dagi Tracker", layout="wide")
st.title("📚 My Scholarship & Job Tracker")

# ========== GITHUB FUNCTIONS WITH DEBUGGING ==========

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
                }
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
            }
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
            st.success("✅ Data saved to GitHub!")
            return True
        else:
            st.error(f"❌ Failed to save: {response.status_code}")
            st.text(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        st.error(f"❌ Error saving: {str(e)}")
        return False

# ========== LOAD DATA ==========

# Force reload from GitHub every time
st.session_state.data = get_data()
data = st.session_state.data

# ========== SIDEBAR ==========

with st.sidebar:
    st.success("✅ Connected to GitHub!")
    st.write(f"📁 Repository: {REPO}")
    
    st.markdown("---")
    
    st.subheader("📊 Stats")
    st.write(f"🎓 Scholarships: {len(data.get('scholarships', []))}")
    st.write(f"💼 Jobs: {len(data.get('jobs', []))}")
    
    st.markdown("---")
    
    # Show last save status
    st.caption("📦 Data saved on GitHub")
    st.caption(f"🔗 github.com/{USER}/{REPO}")

# ========== MASTER CV ==========

st.header("📄 Master CV")

with st.expander("✏️ Edit Your Master CV"):
    cv_title = st.text_input("CV Title", value=data.get('masterCV', {}).get('title', 'My Master CV'))
    cv_content = st.text_area("📝 Paste Your CV", value=data.get('masterCV', {}).get('content', ''), height=150)
    
    if st.button("💾 Save CV", type="primary"):
        data['masterCV']['title'] = cv_title
        data['masterCV']['content'] = cv_content
        data['masterCV']['lastUpdated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if save_data(data):
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
            if save_data(data):
                st.rerun()
        else:
            st.error("❌ Name and Deadline are required!")

# Display Scholarships
scholarships = data.get('scholarships', [])
if scholarships:
    st.subheader(f"📋 Your Scholarships ({len(scholarships)})")
    
    for idx, s in enumerate(scholarships):
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
                        save_data(data)
                        st.rerun()
                if s.get('status') == 'submitted':
                    if st.button("✅ Accept", key=f"s_acc_{idx}"):
                        s['status'] = 'accepted'
                        save_data(data)
                        st.rerun()
                    if st.button("❌ Reject", key=f"s_rej_{idx}"):
                        s['status'] = 'rejected'
                        save_data(data)
                        st.rerun()
                if st.button("🗑️ Delete", key=f"s_del_{idx}"):
                    data['scholarships'].remove(s)
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
            if save_data(data):
                st.rerun()
        else:
            st.error("❌ Title, Company, and Deadline are required!")

# Display Jobs
jobs = data.get('jobs', [])
if jobs:
    st.subheader(f"📋 Your Jobs ({len(jobs)})")
    
    for idx, j in enumerate(jobs):
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
                        save_data(data)
                        st.rerun()
                if j.get('status') == 'submitted':
                    if st.button("✅ Accept", key=f"j_acc_{idx}"):
                        j['status'] = 'accepted'
                        save_data(data)
                        st.rerun()
                    if st.button("❌ Reject", key=f"j_rej_{idx}"):
                        j['status'] = 'rejected'
                        save_data(data)
                        st.rerun()
                if st.button("🗑️ Delete", key=f"j_del_{idx}"):
                    data['jobs'].remove(j)
                    save_data(data)
                    st.rerun()
            st.divider()
else:
    st.info("No jobs yet. Add your first one above!")

# ========== FOOTER ==========

st.markdown("---")
st.caption("🇪🇹 All data saved permanently on GitHub")
st.caption(f"📦 https://github.com/{USER}/{REPO}")
