#!/usr/bin/env bash
set -euo pipefail

API_URL="http://localhost:8000/api/messages/publish"
API_KEY="${API_KEY:-my-super-secret-api-key}"

# Simple one-off publish with a static JSON payload.
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "topic": "devices/device123/telemetry/env_sensor",
    "retain": true,
    "message": {
      "message_id": "msg-001",
      "timestamp": "2024-06-01T12:00:00Z",
      "device_id": "device123",
      "message_type": "telemetry",
      "service_name": "env_sensor",
      "payload": {
        "temperature": 25.5,
        "humidity": 60
      }
    }
  }'

# Example with variables (useful for scripts).
DEVICE_ID="device123"
TEMP=26.2
HUMIDITY=58.4
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{\
    \"topic\": \"devices/${DEVICE_ID}/telemetry/env_sensor\",\
    \"retain\": true,\
    \"message\": {\
      \"message_id\": \"msg-${DEVICE_ID}-${NOW}\",\
      \"timestamp\": \"${NOW}\",\
      \"device_id\": \"${DEVICE_ID}\",\
      \"message_type\": \"telemetry\",\
      \"service_name\": \"env_sensor\",\
      \"payload\": {\
        \"temperature\": ${TEMP},\
        \"humidity\": ${HUMIDITY}\
      }\
    }\
  }"
