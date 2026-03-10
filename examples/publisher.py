import os
import json
import time
import uuid
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_USER = os.getenv("MQTT_USER", "mqttuser")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "mqttpassword")

def publish_telemetry(client):
    topic = "devices/device123/telemetry/env_sensor"
    message = {
        "message_id": f"msg-{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "unix_timestamp": int(time.time()),
        "device_id": "device123",
        "message_type": "telemetry",
        "service_name": "env_sensor",
        "payload": {
            "temperature": 25.5,
            "humidity": 60.2
        }
    }
    
    # Publish with retain=True so new subscribers get the latest state immediately
    client.publish(topic, json.dumps(message), retain=True)
    print(f"Published telemetry to {topic}: {message['message_id']}")

def publish_backup_result(client):
    topic = "devices/server123/backup_result/backup_service"
    message = {
        "message_id": f"msg-{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "unix_timestamp": int(time.time()),
        "device_id": "server123",
        "message_type": "backup_result",
        "service_name": "backup_service",
        "payload": {
            "status": "success",
            "backup_size_mb": 512,
            "duration_seconds": 125
        }
    }
    
    client.publish(topic, json.dumps(message), retain=True)
    print(f"Published backup result to {topic}: {message['message_id']}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    print("Starting publisher... Press Ctrl+C to exit.")
    try:
        while True:
            publish_telemetry(client)
            time.sleep(2)
            publish_backup_result(client)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nPublisher stopped.")
        client.disconnect()