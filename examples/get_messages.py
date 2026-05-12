import urllib.request
import json
import os

API_BASE_URL = "http://localhost:8000/api"
API_KEY = os.getenv("API_KEY", "my-super-secret-api-key")

def get_messages_for_topic_paginated(topic: str):
    print(f"--- Fetching messages for topic: {topic} using pagination ---")
    offset = 0
    limit = 2  # Small limit to demonstrate pagination
    
    while True:
        # Construct URL with query parameters
        url = f"{API_BASE_URL}/messages/get?topic={topic}&limit={limit}&offset={offset}"
        print(f"Requesting messages with offset {offset}...")
        
        try:
            req = urllib.request.Request(url)
            req.add_header("X-API-Key", API_KEY)
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                messages = data.get("messages", [])
                total_count = data.get("total_count", 0)
                message = data.get("message")

                if messages:
                    print(f"Found {len(messages)} messages (Total available: {total_count}):")
                    for msg in messages:
                        print(f"  [{msg.get('time')}] ID: {msg.get('message_id')} | Payload: {json.dumps(msg.get('payload'))}")
                    offset += limit
                else:
                    if message:
                        print(f"End of list: {message}")
                    elif total_count == 0:
                        print("No messages found for this topic.")
                    break
                    
                if offset >= total_count:
                    print("Reached end of available messages.")
                    break

        except urllib.error.URLError as e:
            print(f"HTTP connection error: {e}")
            break

if __name__ == "__main__":
    # Replace with a topic that actually exists in your database
    target_topic = "devices/device123/telemetry/env_sensor"
    get_messages_for_topic_paginated(target_topic)
