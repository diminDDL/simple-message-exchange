import urllib.request
import json
import os

API_BASE_URL = "http://localhost:8000/api"
API_KEY = os.getenv("API_KEY", "my-super-secret-api-key")

def list_all_topics_paginated():
    print("--- Fetching all distinct topics using pagination ---")
    offset = 0
    limit = 1  # Small limit to demonstrate pagination
    
    while True:
        url = f"{API_BASE_URL}/topics/list?limit={limit}&offset={offset}"
        print(f"Requesting topics with offset {offset}...")
        
        try:
            req = urllib.request.Request(url)
            req.add_header("X-API-Key", API_KEY)
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                topics = data.get("topics", [])
                total_count = data.get("total_count", 0)
                message = data.get("message")

                if topics:
                    for topic in topics:
                        print(f"  - {topic}")
                    offset += limit
                else:
                    if message:
                        print(f"End of list: {message}")
                    break
                    
                if offset >= total_count:
                    print("Reached end of available topics.")
                    break

        except urllib.error.URLError as e:
            print(f"HTTP connection error: {e}")
            break

if __name__ == "__main__":
    list_all_topics_paginated()
