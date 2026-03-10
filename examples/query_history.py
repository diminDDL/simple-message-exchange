import urllib.request
import json
import os
import logging

API_URL = "http://localhost:8000/api/messages/recent"
API_KEY = os.getenv("API_KEY", "my-super-secret-api-key")

def query_recent_messages():
    try:
        print("Fetching the 5 most recent messages from HTTP API...")
        req = urllib.request.Request(API_URL)
        req.add_header("X-API-Key", API_KEY)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            messages = data.get("messages", [])
            
            if not messages:
                print("No messages found via the API. Are you running the publisher?")
                
            for msg in messages:
                print(f"\nTime: {msg.get('time')}")
                print(f"Device ID: {msg.get('device_id')} | Type: {msg.get('message_type')}")
                print(f"Topic: {msg.get('topic')}")
                print(f"Payload: {json.dumps(msg.get('payload'), indent=2)}")
                
    except urllib.error.URLError as e:
        print(f"HTTP connection error: {e}")

if __name__ == "__main__":
    query_recent_messages()