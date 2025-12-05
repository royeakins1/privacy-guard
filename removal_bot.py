import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Configuration
QUEUE_FILE = "removal_queue.csv"

def setup_driver():
    """Installs the correct Chrome driver and launches browser"""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Uncomment this to make browser invisible
    
    # improved driver loading using webdriver_manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def process_removal(request):
    """
    This is where the 'Bot' logic lives.
    """
    print(f"🤖 BOT: Starting removal for {request['name']} on {request['broker']}...")
    
    driver = setup_driver()
    
    try:
        # --- BOT LOGIC GOES HERE ---
        
        if request['broker'] == "FastPeopleSearch":
            # Example: Going to the actual removal page
            driver.get("https://www.fastpeoplesearch.com/removal")
            time.sleep(3) # Wait for page to load
            print("   -> Navigated to opt-out page")
            
            # This is where you would use driver.find_element... to fill the form
            # For now, we simulate work:
            time.sleep(2) 
            
        elif request['broker'] == "Whitepages":
            print("   -> Whitepages logic would go here.")
            time.sleep(2)
            
        else:
            print(f"   -> No specific script defined for {request['broker']} yet.")
            time.sleep(1)

        print("✅ BOT: Request processed successfully.")
        
    except Exception as e:
        print(f"❌ BOT: Failed - {e}")
        
    finally:
        driver.quit()

def main():
    print("👀 Watching 'removal_queue.csv' for new requests...")
    print("   (Press Ctrl+C to stop)")
    
    while True:
        if os.path.exists(QUEUE_FILE):
            try:
                df = pd.read_csv(QUEUE_FILE)
                
                # Check if 'status' column exists, if not create it (migration)
                if 'status' not in df.columns:
                    df['status'] = 'pending'
                
                # Find pending rows
                pending = df[df['status'] == 'pending']
                
                if not pending.empty:
                    for index, row in pending.iterrows():
                        process_removal(row)
                        
                        # Mark as done in CSV
                        df.at[index, 'status'] = 'completed'
                        
                        # Save immediately so we don't repeat if crash
                        df.to_csv(QUEUE_FILE, index=False)
                        print(f"   -> Marked {row['name']} as completed in Queue.")
                        
                else:
                    # Just waiting
                    pass
                    
            except Exception as e:
                print(f"Error reading queue file: {e}")
                
        time.sleep(5) # Check every 5 seconds

if __name__ == "__main__":
    main()
