import streamlit as st
import time
import random
import pandas as pd

# --- Configuration ---
st.set_page_config(
    page_title="PrivacyGuard",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Mock Data Database ---
# In a real app, this would be your connection to a database or scraping results
def get_mock_brokers():
    return [
        {"id": 1, "name": "DataSearch4U", "difficulty": "Easy", "status": "exposed", "found": ["Phone", "Address", "Age"]},
        {"id": 2, "name": "PeopleFinder", "difficulty": "Medium", "status": "exposed", "found": ["Full Name", "Relatives"]},
        {"id": 3, "name": "BackgroundCheck", "difficulty": "Hard", "status": "exposed", "found": ["Court Records", "Email"]},
        {"id": 4, "name": "PublicRecords", "difficulty": "Medium", "status": "exposed", "found": ["Address History"]},
        {"id": 5, "name": "InfoBroker", "difficulty": "Easy", "status": "exposed", "found": ["Phone", "Email"]},
    ]

# --- Session State Management ---
# This keeps track of data across button clicks
if 'view' not in st.session_state:
    st.session_state.view = 'onboarding'
if 'brokers' not in st.session_state:
    st.session_state.brokers = []
if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "", "city": "", "state": ""}

# --- Core Logic Functions ---

def simulate_scan():
    """Simulates the visual effect of scanning databases"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    stages = [
        "Connecting to public records databases...",
        f"Searching for '{st.session_state.user_info['name']}'...",
        "Analyzing social media leaks...",
        "Cross-referencing address history...",
        "Querying data broker APIs...",
        "Compiling exposure report..."
    ]
    
    for i in range(101):
        # Update progress bar
        progress_bar.progress(i)
        
        # Update text every 20%
        if i % 20 == 0:
            stage_index = min(i // 20, len(stages) - 1)
            status_text.text(stages[stage_index])
            
        time.sleep(0.02) # Control speed of simulation
    
    time.sleep(0.5)
    st.session_state.brokers = get_mock_brokers()
    st.session_state.view = 'dashboard'
    st.rerun()

def remove_broker(broker_id):
    """Simulates sending a removal request"""
    # Find the broker and update status
    for broker in st.session_state.brokers:
        if broker['id'] == broker_id:
            broker['status'] = 'processing'
            break
            
    # In a real app, this is where you would trigger your Selenium bot:
    # run_removal_bot(broker_name)
    
    st.toast(f"Removal request sent for {broker['name']}!")
    time.sleep(1) # Fake processing time
    
    # Simulate completion
    for broker in st.session_state.brokers:
        if broker['id'] == broker_id:
            broker['status'] = 'removed'
            break
    st.rerun()

def remove_all():
    """Batch removal simulation"""
    count = 0
    for broker in st.session_state.brokers:
        if broker['status'] == 'exposed':
            broker['status'] = 'processing'
            count += 1
    
    st.toast(f"Initiated removal for {count} brokers...")
    time.sleep(2)
    
    for broker in st.session_state.brokers:
        if broker['status'] == 'processing':
            broker['status'] = 'removed'
    st.rerun()

# --- Views ---

def show_onboarding():
    st.markdown("<h1 style='text-align: center;'>🛡️ PrivacyGuard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Your personal data is for sale. We find it and remove it for you.</p>", unsafe_allow_html=True)
    
    st.write("---")
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.session_state.user_info['name'] = st.text_input("Full Name", placeholder="e.g. Sarah Connor")
            
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.user_info['city'] = st.text_input("City", placeholder="Los Angeles")
            with c2:
                st.session_state.user_info['state'] = st.text_input("State", placeholder="CA")
            
            st.write("") # Spacer
            
            # Disable button if name is empty
            btn_disabled = not st.session_state.user_info['name']
            if st.button("Start Free Scan 🔎", type="primary", use_container_width=True, disabled=btn_disabled):
                simulate_scan()
                
    st.write("---")
    st.caption("🔒 Secured with bank-level 256-bit encryption. We do not sell your data.")

def show_dashboard():
    # --- Metrics Section ---
    exposed = sum(1 for b in st.session_state.brokers if b['status'] == 'exposed')
    removed = sum(1 for b in st.session_state.brokers if b['status'] == 'removed')
    
    # Sidebar for navigation/user profile
    with st.sidebar:
        st.title("PrivacyGuard")
        st.success(f"User: {st.session_state.user_info['name']}")
        st.info("Plan: Free Scan")
        if st.button("Reset / New Scan"):
            st.session_state.view = 'onboarding'
            st.rerun()

    # Main Dashboard
    st.title("Scan Results")
    
    # KPIs
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Exposed Records", exposed, delta=f"-{removed}" if removed > 0 else None, delta_color="inverse")
    kpi2.metric("Removal in Progress", 0)
    kpi3.metric("Protected", removed, delta="Active", delta_color="normal")
    
    st.write("---")
    
    col_head, col_btn = st.columns([3, 1])
    with col_head:
        st.subheader("Data Broker Database")
    with col_btn:
        if exposed > 0:
            if st.button("🛡️ Remove All Records"):
                remove_all()
    
    # Broker List
    for broker in st.session_state.brokers:
        with st.container():
            # Create a "card" look using columns
            c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
            
            with c1:
                st.markdown(f"**{broker['name']}**")
                st.caption(f"Difficulty: {broker['difficulty']}")
            
            with c2:
                # Display tags for found data
                tags = [f"`{item}`" for item in broker['found']]
                st.markdown(" ".join(tags))
            
            with c3:
                # Status badges
                if broker['status'] == 'exposed':
                    st.markdown("🔴 **Exposed**")
                elif broker['status'] == 'processing':
                    st.markdown("🟠 *Processing...*")
                else:
                    st.markdown("🟢 **Removed**")
            
            with c4:
                # Action Button
                if broker['status'] == 'exposed':
                    if st.button("Remove", key=f"btn_{broker['id']}"):
                        remove_broker(broker['id'])
                elif broker['status'] == 'removed':
                    st.button("✔ Done", key=f"btn_done_{broker['id']}", disabled=True)
            
            st.divider()

# --- Main App Controller ---
if __name__ == "__main__":
    if st.session_state.view == 'onboarding':
        show_onboarding()
    elif st.session_state.view == 'dashboard':
        show_dashboard()