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
REPO = "scholarship-tracker"
FILE = "data.json"

# Check if token works
if not TOKEN:
    st.error("❌ OOPS! No token found! Create .env file!")
    st.stop()

st.set_page_config(page_title="My Tracker", layout="wide")
st.title("🎯 My Scholarship & Job Tracker")

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
            default = {"scholarships": [], "jobs": []}
            save_data(default)
            return default
    except:
        return {"scholarships": [], "jobs": []}

def save_data(data):
    """Save data to GitHub"""
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
    headers = {'Authorization': f'token {TOKEN}'}
    
    # Get the SHA (GitHub needs this to update)
    sha = None
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            sha = r.json()['sha']
    except:
        pass
    
    # Prepare data
    content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
    payload = {'message': 'Update', 'content': content, 'branch': 'main'}
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
    st.write(f"📁 {REPO}")
    
    st.markdown("---")
    
    # Quick stats
    st.subheader("📊 Stats")
    st.write(f"🎓 Scholarships: {len(data.get('scholarships', []))}")
    st.write(f"💼 Jobs: {len(data.get('jobs', []))}")

# ========== SCHOLARSHIPS ==========

st.header("🎓 Scholarships")

# Add new scholarship
with st.expander("➕ Add New Scholarship"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Scholarship Name*")
        uni = st.text_input("University")
    with col2:
        deadline = st.date_input("Deadline*")
        country = st.text_input("Country")
    
    if st.button("💾 Save Scholarship", type="primary"):
        if name and deadline:
            new_s = {
                "id": str(datetime.now().timestamp()),
                "name": name,
                "uni": uni,
                "deadline": deadline.strftime("%Y-%m-%d"),
                "country": country,
                "status": "active",
                "createdAt": str(datetime.now())
            }
            data['scholarships'].append(new_s)
            if save_data(data):
                st.success("✅ Added!")
                st.rerun()
        else:
            st.error("❌ Name and Deadline are required!")

# Show scholarships
if data.get('scholarships'):
    for s in data['scholarships']:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{s.get('name')}**")
                if s.get('uni'):
                    st.caption(f"🏛️ {s.get('uni')}")
                if s.get('country'):
                    st.caption(f"🌍 {s.get('country')}")
            with col2:
                st.write(f"📅 {s.get('deadline', 'No deadline')}")
                status = s.get('status', 'active')
                if status == 'active':
                    st.write("🟢 Active")
                elif status == 'submitted':
                    st.write("📤 Submitted")
            with col3:
                if s.get('status') == 'active':
                    if st.button("✅ Submit", key=f"s_{s.get('id')}"):
                        s['status'] = 'submitted'
                        if save_data(data):
                            st.success("✅ Submitted!")
                            st.rerun()
                if st.button("🗑️ Delete", key=f"d_{s.get('id')}"):
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
with st.expander("➕ Add New Job"):
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Job Title*")
        company = st.text_input("Company*")
    with col2:
        deadline = st.date_input("Deadline*")
        location = st.text_input("Location")
    
    if st.button("💾 Save Job", type="primary"):
        if title and company and deadline:
            new_j = {
                "id": str(datetime.now().timestamp()),
                "title": title,
                "company": company,
                "deadline": deadline.strftime("%Y-%m-%d"),
                "location": location,
                "status": "active",
                "createdAt": str(datetime.now())
            }
            data['jobs'].append(new_j)
            if save_data(data):
                st.success("✅ Added!")
                st.rerun()
        else:
            st.error("❌ Title, Company, and Deadline are required!")

# Show jobs
if data.get('jobs'):
    for j in data['jobs']:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{j.get('title')}**")
                if j.get('company'):
                    st.caption(f"🏢 {j.get('company')}")
                if j.get('location'):
                    st.caption(f"📍 {j.get('location')}")
            with col2:
                st.write(f"📅 {j.get('deadline', 'No deadline')}")
                status = j.get('status', 'active')
                if status == 'active':
                    st.write("🟢 Active")
                elif status == 'submitted':
                    st.write("📤 Submitted")
            with col3:
                if j.get('status') == 'active':
                    if st.button("✅ Submit", key=f"js_{j.get('id')}"):
                        j['status'] = 'submitted'
                        if save_data(data):
                            st.success("✅ Submitted!")
                            st.rerun()
                if st.button("🗑️ Delete", key=f"jd_{j.get('id')}"):
                    data['jobs'].remove(j)
                    if save_data(data):
                        st.success("🗑️ Deleted!")
                        st.rerun()
            st.divider()
else:
    st.info("No jobs yet. Add your first one above!")