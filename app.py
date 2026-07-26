import streamlit as st
import requests
import json
import base64
import os
from datetime import datetime

# ========== GET TOKEN FROM GITHUB SECRETS ==========

# For GitHub Cloud
try:
    TOKEN = st.secrets["TOKEN"]
except:
    # For local testing (if you have .env file)
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv("GITHUB_TOKEN")

# Your GitHub info
USER = "digitalirrigation-lgtm"
REPO = "dagi"
FILE = "data.json"

# Check if token works
if not TOKEN:
    st.error("❌ OOPS! No token found! Add GITHUB_TOKEN to secrets!")
    st.stop()

st.set_page_config(page_title="📚 Dagi Tracker", layout="wide")
st.title("📚 My Scholarship & Job Tracker")

# ========== GITHUB FUNCTIONS ==========

def get_data():
    """Fetch data from GitHub"""
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
    headers = {'Authorization': f'token {TOKEN}'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()['content']
            decoded = base64.b64decode(content).decode('utf-8')
            return json.loads(decoded)
        else:
            # Create default data if file doesn't exist
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
    """Save data to GitHub"""
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
    headers = {'Authorization': f'token {TOKEN}'}
    
    # Get current file SHA
    sha = None
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            sha = response.json()['sha']
    except:
        pass
    
    # Prepare content
    content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
    payload = {
        'message': f'Update data - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        'content': content,
        'branch': 'main'
    }
    if sha:
        payload['sha'] = sha
    
    try:
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return True
        else:
            st.error(f"❌ Failed to save: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"❌ Error saving: {str(e)}")
        return False

# ========== LOAD DATA ==========

if 'data' not in st.session_state:
    st.session_state.data = get_data()

data = st.session_state.data

# ========== SIDEBAR ==========

with st.sidebar:
    st.success("✅ Connected to GitHub!")
    st.write(f"📁 Repository: {REPO}")
    st.write(f"👤 User: {USER}")
    
    st.markdown("---")
    
    st.subheader("📊 Quick Stats")
    total_scholarships = len(data.get('scholarships', []))
    total_jobs = len(data.get('jobs', []))
    st.write(f"🎓 Scholarships: {total_scholarships}")
    st.write(f"💼 Jobs: {total_jobs}")
    st.write(f"📄 Total: {total_scholarships + total_jobs}")
    
    st.markdown("---")
    st.caption("📦 All data saved permanently on GitHub")
    st.caption(f"🔗 github.com/{USER}/{REPO}")

# ========== MASTER CV ==========

st.header("📄 Master CV")

with st.expander("✏️ Edit Your Master CV", expanded=False):
    cv_title = st.text_input(
        "CV Title",
        value=data.get('masterCV', {}).get('title', 'My Master CV'),
        key="cv_title"
    )
    cv_content = st.text_area(
        "📝 Paste Your CV Content Here",
        value=data.get('masterCV', {}).get('content', ''),
        height=200,
        key="cv_content",
        help="Paste your CV, cover letter, or any important text here!"
    )
    
    if st.button("💾 Save Master CV", type="primary", key="save_cv"):
        if 'masterCV' not in data:
            data['masterCV'] = {}
        data['masterCV']['title'] = cv_title
        data['masterCV']['content'] = cv_content
        data['masterCV']['lastUpdated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if save_data(data):
            st.success("✅ Master CV Saved Permanently on GitHub!")
            st.rerun()
        else:
            st.error("❌ Failed to save CV!")

# Show saved CV
if data.get('masterCV', {}).get('content'):
    st.subheader("📋 Your Saved CV")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Title:** {data['masterCV'].get('title', '')}")
    with col2:
        st.write(f"**Last Updated:** {data['masterCV'].get('lastUpdated', 'Never')}")
    
    with st.expander("👁️ View Full CV"):
        st.text(data['masterCV'].get('content', ''))

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
    
    notes = st.text_area("📝 Notes (IELTS, requirements, documents...)", key="s_notes", height=80)
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
                st.success("✅ Scholarship Saved Permanently on GitHub!")
                st.rerun()
            else:
                st.error("❌ Failed to save!")
        else:
            st.error("❌ Name and Deadline are required!")

# Display Scholarships
scholarships = data.get('scholarships', [])
if scholarships:
    st.subheader(f"📋 Your Scholarships ({len(scholarships)})")
    
    # Filter
    filter_status = st.selectbox(
        "Filter by status",
        ["All", "active", "submitted", "accepted", "rejected"],
        key="s_filter"
    )
    
    filtered = scholarships if filter_status == "All" else [s for s in scholarships if s.get('status') == filter_status]
    sorted_items = sorted(filtered, key=lambda x: x.get('deadline', '9999-12-31'))
    
    for idx, s in enumerate(sorted_items):
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
                status_emoji = {"active": "🟢", "submitted": "📤", "accepted": "✅", "rejected": "❌"}
                st.write(f"{status_emoji.get(status, '')} {status.capitalize()}")
                st.caption(f"Added: {s.get('createdAt', '')}")
            with col3:
                if status == 'active':
                    if st.button("📤 Submit", key=f"s_sub_{idx}"):
                        s['status'] = 'submitted'
                        if save_data(data):
                            st.rerun()
                elif status == 'submitted':
                    if st.button("✅ Accept", key=f"s_acc_{idx}"):
                        s['status'] = 'accepted'
                        if save_data(data):
                            st.rerun()
                    if st.button("❌ Reject", key=f"s_rej_{idx}"):
                        s['status'] = 'rejected'
                        if save_data(data):
                            st.rerun()
                if st.button("🗑️ Delete", key=f"s_del_{idx}"):
                    data['scholarships'].remove(s)
                    if save_data(data):
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
    
    notes = st.text_area("📝 Notes (requirements, contact...)", key="j_notes", height=80)
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
                st.success("✅ Job Saved Permanently on GitHub!")
                st.rerun()
            else:
                st.error("❌ Failed to save!")
        else:
            st.error("❌ Title, Company, and Deadline are required!")

# Display Jobs
jobs = data.get('jobs', [])
if jobs:
    st.subheader(f"📋 Your Jobs ({len(jobs)})")
    
    filter_status = st.selectbox(
        "Filter by status",
        ["All", "active", "submitted", "accepted", "rejected"],
        key="j_filter"
    )
    
    filtered = jobs if filter_status == "All" else [j for j in jobs if j.get('status') == filter_status]
    sorted_items = sorted(filtered, key=lambda x: x.get('deadline', '9999-12-31'))
    
    for idx, j in enumerate(sorted_items):
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
                status_emoji = {"active": "🟢", "submitted": "📤", "accepted": "✅", "rejected": "❌"}
                st.write(f"{status_emoji.get(status, '')} {status.capitalize()}")
                st.caption(f"Added: {j.get('createdAt', '')}")
            with col3:
                if status == 'active':
                    if st.button("📤 Submit", key=f"j_sub_{idx}"):
                        j['status'] = 'submitted'
                        if save_data(data):
                            st.rerun()
                elif status == 'submitted':
                    if st.button("✅ Accept", key=f"j_acc_{idx}"):
                        j['status'] = 'accepted'
                        if save_data(data):
                            st.rerun()
                    if st.button("❌ Reject", key=f"j_rej_{idx}"):
                        j['status'] = 'rejected'
                        if save_data(data):
                            st.rerun()
                if st.button("🗑️ Delete", key=f"j_del_{idx}"):
                    data['jobs'].remove(j)
                    if save_data(data):
                        st.rerun()
            st.divider()
else:
    st.info("No jobs yet. Add your first one above!")

# ========== FOOTER ==========

st.markdown("---")
st.caption("🇪🇹 Built for Ethiopian scholars | All data saved permanently on GitHub")
st.caption(f"📦 Repository: https://github.com/{USER}/{REPO}")
st.caption(f"📄 Data file: https://github.com/{USER}/{REPO}/blob/main/{FILE}")
