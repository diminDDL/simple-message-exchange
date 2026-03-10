import os
import json
import logging
from datetime import datetime, timezone
import time
import paho.mqtt.client as mqtt
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER = os.getenv("MQTT_USER", "mqttuser")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "mqttpassword")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "message_exchange")

def get_db_connection():
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME
            )
            return conn
        except psycopg2.OperationalError as e:
            logger.warning(f"Database not ready yet, retrying in 5 seconds... ({e})")
            time.sleep(5)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"Connected to MQTT broker with result code {rc}")
        client.subscribe("#")
    else:
        logger.error(f"Failed to connect to MQTT broker with result code {rc}")

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode('utf-8')
        data = json.loads(payload_str)
        
        message_id = data.get("message_id", "unknown")
        timestamp_str = data.get("timestamp")
        unix_timestamp = data.get("unix_timestamp", "unknown")
        device_id = data.get("device_id", "unknown")
        message_type = data.get("message_type", "unknown")
        service_name = data.get("service_name", "unknown")
        payload = data.get("payload", {})
        
        # Auto handle different timestamp formats and fall back to current time if missing
        if unix_timestamp != "unknown":
            timestamp = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
        elif timestamp_str:
            # Handle ISO formatting
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1] + '+00:00'
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = datetime.now(timezone.utc)
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_query = """
            INSERT INTO messages (time, message_id, device_id, message_type, service_name, topic, payload)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            timestamp, message_id, device_id, message_type, service_name, msg.topic, json.dumps(payload)
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Inserted message {message_id} from topic {msg.topic}")
        
    except json.JSONDecodeError:
        logger.warning(f"Could not parse payload as JSON from topic {msg.topic}. Skipping.")
    except Exception as e:
        logger.error(f"Error processing message from topic {msg.topic}: {e}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            break
        except Exception as e:
            logger.warning(f"MQTT broker not ready, retrying in 5 seconds... ({e})")
            time.sleep(5)
            
    logger.info("Starting MQTT loop...")
    client.loop_forever()