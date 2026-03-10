import os
import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_USER = os.getenv("MQTT_USER", "mqttuser")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "mqttpassword")

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    # Subscribe to all device topics
    topic = "devices/#"
    client.subscribe(topic)
    print(f"Subscribed to topic: {topic}")
    print("Waiting for messages...")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"\n--- New Message on {msg.topic} ---")
        print(json.dumps(payload, indent=2))
    except json.JSONDecodeError:
        print(f"Received non-JSON message on {msg.topic}: {msg.payload}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nSubscriber stopped.")
        client.disconnect()