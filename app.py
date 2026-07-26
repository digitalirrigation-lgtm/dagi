import streamlit as st
import requests
import json
import base64
from datetime import datetime

# ========== GET TOKEN FROM STREAMLIT SECRETS ==========

# Try to get token from secrets
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
    st.error("❌ No token found! Please add TOKEN to Streamlit secrets.")
    st.info("Go to Settings → Secrets and add: TOKEN = 'your_token_here'")
    st.stop()

st.set_page_config(page_title="📚 Dagi Tracker", layout="wide")
st.title("📚 My Scholarship & Job Tracker")
st.success("✅ Connected to GitHub!")

# ========== GITHUB FUNCTIONS ==========

def get_data():
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
    headers = {'Authorization': f'token {TOKEN}'}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json()['content']
            decoded = base64.b64decode(content).decode('utf-8')
            return json.loads(decoded)
        else:
            default_data = {"scholarships": [], "jobs": [], "masterCV": {"title": "My Master CV", "content": "", "lastUpdated": ""}}
            save_data(default_data)
            return default_data
    except:
        return {"scholarships": [], "jobs": [], "masterCV": {"title": "My Master CV", "content": "", "lastUpdated": ""}}

def save_data(data):
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{FILE}"
    headers = {'Authorization': f'token {TOKEN}'}
    
    sha = None
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            sha = response.json()['sha']
    except:
        pass
    
    content = base64.b64encode(json.dumps(data, indent=2).encode()).decode()
    payload = {'message': 'Update data', 'content': content, 'branch': 'main'}
    if sha:
        payload['sha'] = sha
    
    try:
        response = requests.put(url, headers=headers, json=payload)
        return response.status_code in [200, 201]
    except:
        return False

# ========== LOAD DATA ==========

if 'data' not in st.session_state:
    st.session_state.data = get_data()

data = st.session_state.data

# ========== SIDEBAR ==========

with st.sidebar:
    st.write(f"📁 Repository: {REPO}")
    st.write(f"👤 User: {USER}")
    st.markdown("---")
    st.subheader("📊 Stats")
    st.write(f"🎓 Scholarships: {len(data.get('scholarships', []))}")
    st.write(f"💼 Jobs: {len(data.get('jobs', []))}")

# ========== MASTER CV ==========

st.header("📄 Master CV")

with st.expander("✏️ Edit Your Master CV"):
    cv_title = st.text_input("CV Title", value=data.get('masterCV', {}).get('title', 'My Master CV'))
    cv_content = st.text_area("📝 Paste Your CV", value=data.get('masterCV', {}).get('content', ''), height=150)
    
    if st.button("💾 Save CV"):
        data['masterCV']['title'] = cv_title
        data['masterCV']['content'] = cv_content
        data['masterCV']['lastUpdated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if save_data(data):
            st.success("✅ CV Saved!")
            st.rerun()

# ========== SCHOLARSHIPS ==========

st.header("🎓 Scholarships")

with st.expander("➕ Add Scholarship"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name *")
        uni = st.text_input("University")
    with col2:
        deadline = st.date_input("Deadline *")
        country = st.text_input("Country")
    
    notes = st.text_area("Notes")
    
    if st.button("💾 Save Scholarship"):
        if name and deadline:
            new_s = {
                "id": str(datetime.now().timestamp()),
                "name": name,
                "uni": uni or "",
                "deadline": deadline.strftime("%Y-%m-%d"),
                "country": country or "",
                "notes": notes or "",
                "status": "active",
                "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            data['scholarships'].append(new_s)
            if save_data(data):
                st.success("✅ Saved!")
                st.rerun()

# Show scholarships
for s in data.get('scholarships', []):
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{s.get('name')}**")
            if s.get('uni'):
                st.caption(f"🏛️ {s.get('uni')}")
            if s.get('country'):
                st.caption(f"🌍 {s.get('country')}")
            if s.get('notes'):
                st.caption(f"📝 {s.get('notes')}")
        with col2:
            st.write(f"📅 {s.get('deadline')}")
            status = s.get('status', 'active')
            if status == 'active':
                if st.button("✅ Submit", key=f"s_{s.get('id')}"):
                    s['status'] = 'submitted'
                    save_data(data)
                    st.rerun()
            else:
                st.write("📤 Submitted")
        st.divider()

# ========== JOBS ==========

st.header("💼 Jobs")

with st.expander("➕ Add Job"):
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Job Title *")
        company = st.text_input("Company *")
    with col2:
        deadline = st.date_input("Deadline *")
        location = st.text_input("Location")
    
    notes = st.text_area("Notes")
    
    if st.button("💾 Save Job"):
        if title and company and deadline:
            new_j = {
                "id": str(datetime.now().timestamp()),
                "title": title,
                "company": company,
                "deadline": deadline.strftime("%Y-%m-%d"),
                "location": location or "",
                "notes": notes or "",
                "status": "active",
                "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            data['jobs'].append(new_j)
            if save_data(data):
                st.success("✅ Saved!")
                st.rerun()

# Show jobs
for j in data.get('jobs', []):
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{j.get('title')}**")
            if j.get('company'):
                st.caption(f"🏢 {j.get('company')}")
            if j.get('location'):
                st.caption(f"📍 {j.get('location')}")
            if j.get('notes'):
                st.caption(f"📝 {j.get('notes')}")
        with col2:
            st.write(f"📅 {j.get('deadline')}")
            status = j.get('status', 'active')
            if status == 'active':
                if st.button("✅ Submit", key=f"j_{j.get('id')}"):
                    j['status'] = 'submitted'
                    save_data(data)
                    st.rerun()
            else:
                st.write("📤 Submitted")
        st.divider()

st.caption("📦 All data saved permanently on GitHub")
