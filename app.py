import streamlit as st
import requests
import json
import base64
import os
from datetime import datetime
from dotenv import load_dotenv

# Load your secret token
load_dotenv('.env.txt')

# Your GitHub info
TOKEN = os.getenv("GITHUB_TOKEN")
USER = "digitalirrigation-lgtm"
REPO = "dagi"
FILE = "data.json"

# Check if token works
if not TOKEN:
    st.error("❌ OOPS! No token found! Create .env file!")
    st.stop()

st.set_page_config(page_title="📚 Dagi Tracker", layout="wide")
st.title("📚 My Scholarship & Job Tracker")

# ========== GITHUB FUNCTIONS ==========

def get_data():
    """Get data from GitHub"""
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
    headers = {'Authorization': f'token {TOKEN}'}
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            content = r.json()['content']
            decoded = base64.b64decode(content).decode('utf-8')
            return json.loads(decoded)
        else:
            # If file doesn't exist, create it
            default = {"scholarships": [], "jobs": [], "masterCV": {"title": "My Master CV", "content": "", "lastUpdated": ""}}
            save_data(default)
            return default
    except:
        return {"scholarships": [], "jobs": [], "masterCV": {"title": "My Master CV", "content": "", "lastUpdated": ""}}

def save_data(data):
    """Save data to GitHub"""
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
    headers = {'Authorization': f'token {TOKEN}'}
    
    # Get the SHA
    sha = None
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            sha = r.json()['sha']
    except:
        pass
    
    # Prepare data
    content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
    payload = {'message': 'Update data', 'content': content, 'branch': 'main'}
    if sha:
        payload['sha'] = sha
    
    # Save
    r = requests.put(url, headers=headers, json=payload)
    return r.status_code in [200, 201]

# ========== LOAD DATA ==========

if 'data' not in st.session_state:
    st.session_state.data = get_data()

data = st.session_state.data

# ========== SIDEBAR ==========

with st.sidebar:
    st.success("✅ Connected to GitHub!")
    st.write(f"📁 Repository: {REPO}")
    
    st.markdown("---")
    
    # Quick stats
    st.subheader("📊 Stats")
    st.write(f"🎓 Scholarships: {len(data.get('scholarships', []))}")
    st.write(f"💼 Jobs: {len(data.get('jobs', []))}")
    
    st.markdown("---")
    st.caption("📦 All data saved on GitHub")
    st.caption("🔗 https://github.com/digitalirrigation-lgtm/dagi")

# ========== MASTER CV SECTION ==========

st.header("📄 Master CV")

with st.expander("✏️ Edit Your Master CV", expanded=True):
    cv_title = st.text_input("CV Title", value=data.get('masterCV', {}).get('title', 'My Master CV'))
    cv_content = st.text_area("📝 Paste Your CV Content Here", 
                               value=data.get('masterCV', {}).get('content', ''),
                               height=200,
                               help="Paste your CV, cover letter, or any text you want to save permanently!")
    
    if st.button("💾 Save Master CV", type="primary"):
        if 'masterCV' not in data:
            data['masterCV'] = {}
        data['masterCV']['title'] = cv_title
        data['masterCV']['content'] = cv_content
        data['masterCV']['lastUpdated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if save_data(data):
            st.success("✅ Master CV Saved Permanently on GitHub!")
            st.rerun()

# Show current CV
if data.get('masterCV', {}).get('content'):
    st.subheader("📋 Your Saved CV")
    st.write(f"**Title:** {data['masterCV'].get('title', '')}")
    st.write(f"**Last Updated:** {data['masterCV'].get('lastUpdated', 'Never')}")
    with st.expander("👁️ View CV"):
        st.text(data['masterCV'].get('content', ''))

# ========== SCHOLARSHIPS ==========

st.header("🎓 Scholarships")

# Add new scholarship
with st.expander("➕ Add New Scholarship", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Scholarship Name*", key="s_name")
        uni = st.text_input("University/Organization", key="s_uni")
    with col2:
        deadline = st.date_input("Deadline*", key="scholarship_deadline")
        country = st.text_input("Country", key="s_country")
    
    notes = st.text_area("📝 Notes (IELTS, requirements, documents...)", key="s_notes", height=80)
    link = st.text_input("🔗 Application Link", key="s_link")
    
    if st.button("💾 Save Scholarship", type="primary", key="save_scholarship"):
        if name and deadline:
            new_s = {
                "id": str(datetime.now().timestamp()),
                "name": name,
                "uni": uni,
                "deadline": deadline.strftime("%Y-%m-%d"),
                "country": country,
                "notes": notes,
                "link": link,
                "status": "active",
                "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            data['scholarships'].append(new_s)
            if save_data(data):
                st.success("✅ Scholarship Saved Permanently on GitHub!")
                st.rerun()
        else:
            st.error("❌ Name and Deadline are required!")

# Show scholarships
if data.get('scholarships'):
    st.subheader(f"📋 Your Scholarships ({len(data['scholarships'])})")
    
    # Sort by deadline
    sorted_scholarships = sorted(data['scholarships'], key=lambda x: x.get('deadline', '9999-12-31'))
    
    for idx, s in enumerate(sorted_scholarships):
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{s.get('name')}**")
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
                st.caption(f"📅 Added: {s.get('createdAt', '')}")
            with col3:
                if s.get('status') == 'active':
                    if st.button("📤 Submit", key=f"s_submit_{idx}"):
                        s['status'] = 'submitted'
                        if save_data(data):
                            st.success("✅ Marked as submitted!")
                            st.rerun()
                if s.get('status') == 'submitted':
                    if st.button("✅ Accept", key=f"s_accept_{idx}"):
                        s['status'] = 'accepted'
                        if save_data(data):
                            st.success("✅ Marked as accepted!")
                            st.rerun()
                    if st.button("❌ Reject", key=f"s_reject_{idx}"):
                        s['status'] = 'rejected'
                        if save_data(data):
                            st.success("❌ Marked as rejected!")
                            st.rerun()
                if st.button("🗑️ Delete", key=f"s_del_{idx}"):
                    data['scholarships'].remove(s)
                    if save_data(data):
                        st.success("🗑️ Deleted!")
                        st.rerun()
            st.divider()
else:
    st.info("No scholarships yet. Add your first one above!")

# ========== JOBS ==========

st.header("💼 Jobs")

# Add new job
with st.expander("➕ Add New Job", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Job Title*", key="j_title")
        company = st.text_input("Company*", key="j_company")
    with col2:
        deadline = st.date_input("Deadline*", key="job_deadline")
        location = st.text_input("Location", key="j_location")
    
    notes = st.text_area("📝 Notes (requirements, contact...)", key="j_notes", height=80)
    link = st.text_input("🔗 Application Link", key="j_link")
    
    if st.button("💾 Save Job", type="primary", key="save_job"):
        if title and company and deadline:
            new_j = {
                "id": str(datetime.now().timestamp()),
                "title": title,
                "company": company,
                "deadline": deadline.strftime("%Y-%m-%d"),
                "location": location,
                "notes": notes,
                "link": link,
                "status": "active",
                "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            data['jobs'].append(new_j)
            if save_data(data):
                st.success("✅ Job Saved Permanently on GitHub!")
                st.rerun()
        else:
            st.error("❌ Title, Company, and Deadline are required!")

# Show jobs
if data.get('jobs'):
    st.subheader(f"📋 Your Jobs ({len(data['jobs'])})")
    
    sorted_jobs = sorted(data['jobs'], key=lambda x: x.get('deadline', '9999-12-31'))
    
    for idx, j in enumerate(sorted_jobs):
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{j.get('title')}**")
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
                st.caption(f"📅 Added: {j.get('createdAt', '')}")
            with col3:
                if j.get('status') == 'active':
                    if st.button("📤 Submit", key=f"j_submit_{idx}"):
                        j['status'] = 'submitted'
                        if save_data(data):
                            st.success("✅ Marked as submitted!")
                            st.rerun()
                if j.get('status') == 'submitted':
                    if st.button("✅ Accept", key=f"j_accept_{idx}"):
                        j['status'] = 'accepted'
                        if save_data(data):
                            st.success("✅ Marked as accepted!")
                            st.rerun()
                    if st.button("❌ Reject", key=f"j_reject_{idx}"):
                        j['status'] = 'rejected'
                        if save_data(data):
                            st.success("❌ Marked as rejected!")
                            st.rerun()
                if st.button("🗑️ Delete", key=f"j_del_{idx}"):
                    data['jobs'].remove(j)
                    if save_data(data):
                        st.success("🗑️ Deleted!")
                        st.rerun()
            st.divider()
else:
    st.info("No jobs yet. Add your first one above!")

# ========== FOOTER ==========

st.markdown("---")
st.caption("🇪🇹 Built for Ethiopian scholars | All data saved permanently on GitHub")
st.caption(f"📦 Repository: https://github.com/digitalirrigation-lgtm/dagi")
