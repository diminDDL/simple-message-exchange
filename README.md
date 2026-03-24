# simple-message-exchange

This is a simple message exchange system for sending and receiving telemetry and event messages between embedded devices, servers, and clients. Built based on the needs of my homelab spanning many devices across different locations and my desire to consolidate their states into one place. As well as being able to monitor and query data using anything spanning from an MCU to a server.

The system uses MQTT for low-latency live message delivery and TimescaleDB for persistent storage of historical messages. MQTT provides topic-based pub/sub and supports retained messages for latest-known state, while TimescaleDB stores message history for querying, replay, and catch-up after clients have been offline.

This architecture is intended to support both:

* **live subscriptions** to current updates
* **historical retrieval** of past messages when needed

For example, when a client subscribes to a topic, it can receive the latest retained message for that topic and then continue receiving new live updates. If the client needs older messages or missed updates from a previous period offline, those can be retrieved from TimescaleDB.

## Typical message format

For a sensor update:

```json
{
  "message_id": "msg-001",
  "timestamp": "2026-03-24T10:26:22.353Z", // Or unix_timestamp: 1774347982
  "device_id": "device123",
  "message_type": "telemetry",
  "service_name": "env_sensor",
  "payload": {
    "temperature": 25.5,
    "humidity": 60
  }
}
```

For a server backup result:

```json
{
  "message_id": "msg-002",
  "timestamp": "2026-03-24T10:26:22.353Z", // Or unix_timestamp: 1774347982
  "device_id": "server123",
  "message_type": "backup_result",
  "service_name": "backup_service",
  "payload": {
    "status": "success",
    "backup_size_mb": 500,
    "duration_seconds": 120
  }
}
```

This format is not strictly enforced and any missing fields will be filled with `unknown`. Here is a list of fields that the system expects, but the only thing you really need is the `payload` field which can be any JSON object.

| Field Name | Description |
|------------|-------------|
| `message_id` | A unique identifier for the message (optional, doesn't have to be unique) |
| `timestamp` | The time the message was created in a string of ISO 8601 format (optional, can be auto-generated) |
| `unix_timestamp` | The time the message was created in Unix timestamp format (optional, can be auto-generated) |
| `device_id` | An identifier for the device or service sending the message (optional) |
| `message_type` | A string categorizing the type of message (optional) |
| `service_name` | A string indicating the specific service or sensor related to the message (optional) |
| `payload` | A JSON object containing the actual data of the message (required) |

## Topics

Each device should have its own topic namespace structured as `devices/{device_id}/{message_type}/{service_name}`. This, however, is just a suggestion and the system will work with any topic structure, and allow any authenticated client to publish and subscribe to any topic.

For example:

* `devices/device123/telemetry/env_sensor`
* `devices/server123/backup_result/backup_service`

A client subscribing to one of these topics can receive the latest retained message for that topic *(if the message was published with the `retain` flag)*, followed by any new live messages published afterward. Historical messages are stored separately in TimescaleDB and can be queried when replay or catch-up is needed through an HTTP API.

## Auto cleanup

The database can be configured to either retain all data indefinitely or automatically delete messages older than a certain age (e.g., 30 days). This is implemented using TimescaleDB's built-in data retention policies. You can enable it by uncommenting the relevant line in `database/init.sql` to add a retention policy that automatically deletes messages older than 30 days (configurable).

**This can only be set during initialization, so if you want to change it you will need to delete the database volume and reinitialize it!**

## Setup & Deployment

This project uses Docker Compose to orchestrate the server side. 

### 0. Prerequisites
Make sure you have Docker and Docker Compose installed on your system.

Also, pull the latest version of this repository to your local machine:
```bash
git clone https://github.com/diminDDL/simple-message-exchange
```
and enter the project directory:

```bash
cd simple-message-exchange
```

### 1. Configure the Environment
First, configure your credentials by copying the `.env.example` file:
```bash
cp .env.example .env
```
Edit `.env` to set your desired MQTT passwords, database credentials, and REST API Key.

> *Note:* You can use `pwgen -s -B 32 -n 1` or `openssl rand -base64 32` to generate random API keys and passwords.

### 2. Start the Stack
To build and start the entire stack (Mosquitto Broker, TimescaleDB, Python Bridge, and HTTP API) simply run:
```bash
docker compose up -d --build
```

The system will start out using the resource limits defined in `docker-compose.yml` if you run up against them you can modify the `deploy:` sections. Once started, Mosquitto listens on `:1883` and the REST API listens on `:8000`. TimescaleDB is firewalled behind the Docker network since the clients don't need to access it directly.

## Updating
To update the system, simply enter the project directory and pull the latest changes from the repository and then rebuild the stack:
```bash
git pull
docker compose down
docker compose up -d --build
```

## How to use (Examples)

The `examples/` directory contains Python scripts showing how to talk to both the real-time MQTT broker and the HTTP Historical API.

First, install the example dependencies:
```bash
pip install paho-mqtt
```

### Publishing Messages
When a given device or service wants to publish something, it connects to MQTT and sends its JSON:
```bash
# This will constantly publish sample messages to topics
python examples/publisher.py
```

You can also publish updates over HTTP with `curl`, which is handy for bash scripts. The API will forward the message to MQTT (so live subscribers receive it) and the bridge will store it in TimescaleDB.
See [examples/publish.sh](blob/main/examples/publish.sh) for curl-based publish examples.

### Listening to Live Messages
To listen to messages in real-time, subscribe to specific topics via MQTT:
```bash
# This subscribes to real-time events over MQTT
python examples/subscriber.py
```

### Querying the History
Offline devices needing to "catch-up" on missed events should query the history API endpoint using the required `X-API-Key` defined in the `.env`:
```bash
# This uses the API at http://localhost:8000/api/messages/recent to query history
python examples/query_history.py
```
If you only need the latest message, then MQTT is sufficient if the publishers set the `retain=True` flag when publishing. This way, new subscribers will immediately receive the latest message for that topic upon subscribing.
