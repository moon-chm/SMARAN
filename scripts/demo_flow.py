import requests
import json
import time

API_BASE_URL = "http://localhost:8000/api"

def print_separator():
    print("\n" + "="*60 + "\n")

def run_demo_flow():
    print("🚀 SMARAN PHASE 12 DEMO FLOW SCRIPT")
    print_separator()
    
    # Authenticate
    print("🔑 Authenticating as Caregiver...")
    res_auth = requests.post(f"{API_BASE_URL}/auth/login", data={"username":"caregiver_demo", "password":"password123"})
    if res_auth.status_code != 200:
        print("Authentication failed. Is the API running?")
        return
    token = res_auth.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    elder_id = "ramesh_72"
    
    print_separator()
    # Step 1: Ingest Memory
    print("STEP 1: Ingesting a new memory...")
    memory_text = "Ramesh loves drinking warm milk with turmeric before bed, it makes him happy."
    payload = {"elder_id": elder_id, "text": memory_text, "source_type": "demo_script"}
    start_time = time.time()
    res_ingest = requests.post(f"{API_BASE_URL}/memory/ingest", json=payload, headers=headers)
    ingest_time = round((time.time() - start_time) * 1000, 2)
    
    print(f"Payload sent: '{memory_text}'")
    if res_ingest.status_code == 200:
        data = res_ingest.json()
        print(f"✅ Ingestion successful in {ingest_time}ms")
        print(f"Nodes Created: {json.dumps(data.get('created_nodes'), indent=2)}")
    else:
        print(f"❌ Failed ingestion: {res_ingest.text}")

    print_separator()
    # Step 2 & 3: Chat Interaction & Display Outputs
    print("STEP 2 & 3: Elder Chat Interaction (Requesting Audio)")
    message = "I am feeling a bit restless tonight. What did I usually drink before bed?"
    print(f"Elder Message: '{message}'")
    
    chat_payload = {
        "elder_id": elder_id,
        "message": message,
        "return_audio": False # Disabling actual raw bytes output in terminal for clean logging, but API executes same pipeline
    }
    
    start_chat_time = time.time()
    res_chat = requests.post(f"{API_BASE_URL}/chat", json=chat_payload, headers=headers)
    total_chat_time = round((time.time() - start_chat_time) * 1000, 2)
    
    if res_chat.status_code == 200:
        chat_data = res_chat.json()
        
        print("\n--- RESULTS ---")
        print(f"🤖 LLM Reply: {chat_data.get('reply')}")
        print(f"🎭 Detected Mood: {chat_data.get('detected_mood')} (Confidence: {chat_data.get('mood_confidence')})")
        print(f"⚡ Context Retrieval Latency: {chat_data.get('retrieval_time_ms')} ms")
        print(f"⏱️ Total Response Generation Latency: {total_chat_time} ms")
        print(f"🌟 MoodMitra Triggered: {chat_data.get('moodmitra_recommendation')}")
        print("🎵 Audio Stream Ready (Visible in UI)")
    else:
        print(f"❌ Failed chat: {res_chat.text}")
        
    print_separator()
    print("Demo flow execution completed.")

if __name__ == "__main__":
    run_demo_flow()
