import streamlit as st
import pandas as pd
import time
import os
# The library name is googlesearch-python, but we import it as 'googlesearch'
from googlesearch import search

# --- Configuration ---
st.set_page_config(page_title="PrivacyGuard", page_icon="🛡️")

# --- Database / File Handling ---
QUEUE_FILE = "removal_queue.csv"

def save_to_queue(user_info, broker_name):
    """Saves a removal request to a CSV file"""
    new_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "name": user_info['name'],
        "city": user_info['city'],
        "state": user_info['state'],
        "broker": broker_name,
        "status": "pending"
    }
    
    # Load existing or create new
    if os.path.exists(QUEUE_FILE):
        df = pd.read_csv(QUEUE_FILE)
        # Avoid duplicates: Check if this name+broker combo already exists
        # We convert to string to ensure safe comparison
        is_duplicate = ((df['name'].astype(str) == str(new_entry['name'])) & 
                        (df['broker'].astype(str) == str(broker_name))).any()
        
        if not is_duplicate:
            # Append new entry
            new_df = pd.DataFrame([new_entry])
            df = pd.concat([df, new_df], ignore_index=True)
            df.to_csv(QUEUE_FILE, index=False)
    else:
        # Create new file
        pd.DataFrame([new_entry]).to_csv(QUEUE_FILE, index=False)

# --- Real Scanning Logic ---
def perform_live_scan(name, city, state):
    """
    Real Google Search to find if profiles exist.
    """
    
    # List of common brokers and their domains
    targets = [
        {"name": "Whitepages", "domain": "whitepages.com", "difficulty": "Hard"},
        {"name": "Spokeo", "domain": "spokeo.com", "difficulty": "Medium"},
        {"name": "BeenVerified", "domain": "beenverified.com", "difficulty": "Medium"},
        {"name": "Radaris", "domain": "radaris.com", "difficulty": "Hard"},
        {"name": "FastPeopleSearch", "domain": "fastpeoplesearch.com", "difficulty": "Easy"},
    ]
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, target in enumerate(targets):
        # Update UI
        progress = int((i / len(targets)) * 100)
        progress_bar.progress(progress)
        status_text.text(f"Scanning {target['name']}...")
        
        # Construct the "Google Dork" query
        # Example: site:whitepages.com "John Doe" "Los Angeles"
        query = f'site:{target["domain"]} "{name}" "{city}" "{state}"'
        
        found = False
        found_url = None
        
        try:
            # num_results=1: We only need 1 result to prove exposure
            # sleep_interval=2: Wait 2 seconds between searches to prevent blocking
            search_results = list(search(query, num_results=1, sleep_interval=2))
            if len(search_results) > 0:
                found = True
                found_url = search_results[0]
        except Exception as e:
            print(f"Error scanning {target['name']}: {e}")
            # If error, we assume false to be safe, or you could flag as 'error'
            found = False
            
        if found:
            results.append({
                "id": i,
                "name": target['name'],
                "difficulty": target['difficulty'],
                "status": "exposed",
                "found": ["Public Profile"],
                "url": found_url
            })
            
    progress_bar.progress(100)
    status_text.text("Scan Complete.")
    time.sleep(1)
    return results

# --- Session State ---
if 'view' not in st.session_state:
    st.session_state.view = 'onboarding'
if 'brokers' not in st.session_state:
    st.session_state.brokers = []
if 'user_info' not in st.session_state:
    st.session_state.user_info = {"name": "", "city": "", "state": ""}

# --- Views ---
def show_onboarding():
    st.title("🛡️ PrivacyGuard Live")
    st.info("Now performing REAL Google searches.")
    
    with st.form("scan_form"):
        st.session_state.user_info['name'] = st.text_input("Full Name")
        c1, c2 = st.columns(2)
        st.session_state.user_info['city'] = c1.text_input("City")
        st.session_state.user_info['state'] = c2.text_input("State")
        
        if st.form_submit_button("Start Real Scan"):
            if st.session_state.user_info['name']:
                # Run the scan
                st.session_state.brokers = perform_live_scan(
                    st.session_state.user_info['name'],
                    st.session_state.user_info['city'],
                    st.session_state.user_info['state']
                )
                st.session_state.view = 'dashboard'
                st.rerun()

def show_dashboard():
    st.sidebar.title("Admin Panel")
    if st.sidebar.button("Back to Search"):
        st.session_state.view = 'onboarding'
        st.rerun()
        
    # Show Queue Status (Admin View)
    if os.path.exists(QUEUE_FILE):
        try:
            df = pd.read_csv(QUEUE_FILE)
            queue_count = len(df)
            st.sidebar.metric("Requests in Queue", queue_count)
            if st.sidebar.checkbox("Show Raw Queue Data"):
                st.sidebar.dataframe(df)
        except:
            st.sidebar.error("Could not read queue file.")

    st.title("Scan Results")
    
    if not st.session_state.brokers:
        st.success("No records found! (Or Google blocked the scan)")
        return

    for broker in st.session_state.brokers:
        with st.container():
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                st.subheader(broker['name'])
                if broker.get('url'):
                    st.caption(f"Source: {broker['url'][:40]}...")
            with c2:
                # If the user clicked remove, this broker is technically "exposed" 
                # but might be in the queue. We don't track that perfectly in session state yet.
                if broker['status'] == 'exposed':
                    st.error("Exposed")
                else:
                    st.success("Queued")
            with c3:
                if broker['status'] == 'exposed':
                    # Use a unique key for every button
                    if st.button(f"Remove Data", key=f"btn_{broker['name']}"):
                        # Save to file
                        save_to_queue(st.session_state.user_info, broker['name'])
                        broker['status'] = 'queued'
                        st.toast(f"Added {broker['name']} to removal queue!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.button("Processing...", disabled=True, key=f"btn_done_{broker['name']}")
            st.divider()

if __name__ == "__main__":
    if st.session_state.view == 'onboarding':
        show_onboarding()
    elif st.session_state.view == 'dashboard':
        show_dashboard()
