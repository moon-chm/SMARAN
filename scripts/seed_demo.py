import requests
import time
import sys
import wave
import struct
import math
import os

API_BASE_URL = os.getenv("API_URL", "http://localhost:8000/api")

def wait_for_api():
    print("Waiting for API to be ready...")
    for _ in range(30):
        try:
            res = requests.get(f"{API_BASE_URL}/auth/login")
            if res.status_code in [200, 405, 422]:
                print("API is ready!")
                return True
        except:
            pass
        time.sleep(2)
    print("API failed to boot in time. Exiting seed script.")
    sys.exit(1)

def get_token():
    res = requests.post(f"{API_BASE_URL}/auth/login", data={"username": "caregiver_demo", "password": "password123"})
    if res.status_code == 200:
        return res.json()["access_token"]
    else:
        print(f"Auth failed during seed: {res.text}")
        sys.exit(1)

def create_demo_wav(filename):
    sample_rate = 44100
    duration = 3.0
    frequency = 440.0
    with wave.open(filename, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(int(sample_rate * duration)):
            value = int(32767.0 * math.sin(frequency * math.pi * 2 * i / sample_rate))
            data = struct.pack('<h', value)
            wav_file.writeframesraw(data)

def seed_data():
    wait_for_api()
        
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    elder_id = "elder_123"
    
    # 1. Seed Voice Profile
    wav_path = "ramesh_demo.wav"
    create_demo_wav(wav_path)
    
    print("Uploading dummy voice profile...")
    with open(wav_path, "rb") as f:
        files = {"file": ("ramesh_demo.wav", f, "audio/wav")}
        data = {"elder_id": elder_id}
        res = requests.post(f"{API_BASE_URL}/voice/upload", files=files, data=data, headers=headers)
        print(f" -> Voice upload: {res.status_code}")
        
    os.remove(wav_path)
    
    # 2. Seed memory data points
    memories = [
        "Doctor prescribed 500mg of Metformin daily for diabetes.",
        "Ramesh has to take Aspirin 100mg once daily in the morning.",
        "Ramesh has an appointment with Dr. Gupta next Tuesday at 10 AM.",
        "Ramesh has an appointment for a flu shot at the clinic next Friday.",
        "Ramesh has been feeling dizzy and nauseous every morning.",
        "He has been complaining of minor back pain.",
        "He feels very lonely when his son doesn't visit him on weekends.",
        "Ramesh was very anxious about his finances yesterday.",
        "Ramesh loves listening to old Bollywood songs from the 1970s."
    ]
    
    print(f"Seeding {len(memories)} memory points for Elder {elder_id}...")
    for mem in memories:
        payload = {"elder_id": elder_id, "text": mem, "source_type": "caregiver_input"}
        res = requests.post(f"{API_BASE_URL}/memory/ingest", json=payload, headers=headers)
        if res.status_code == 200:
            print(f" -> Processed: {mem[:50]}...")
        else:
            print(f" -> Error on {mem[:50]}: {res.text}")
            
    print("\n✅ Seed completed successfully!")

if __name__ == "__main__":
    seed_data()