# simple-message-exchange

This is a simple message exchange system for sending and receiving telemetry and event messages between embedded devices, servers, and clients.

The system uses **MQTT** for low-latency live message delivery and **TimescaleDB** for persistent storage of historical messages. MQTT provides topic-based pub/sub and supports retained messages for latest-known state, while TimescaleDB stores message history for querying, replay, and catch-up after clients have been offline.

This architecture is intended to support both:

* **live subscriptions** to current updates
* **historical retrieval** of past messages when needed

For example, when a client subscribes to a topic, it can receive the latest retained message for that topic and then continue receiving new live updates. If the client needs older messages or missed updates from a previous period offline, those can be retrieved from TimescaleDB.

## Typical message format

For a sensor update:

```json
{
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
```

For a server backup result:

```json
{
  "message_id": "msg-002",
  "timestamp": "2024-06-01T12:00:00Z",
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

## Topics

Each device generally has its own topic namespace, and clients can subscribe to the topics they are interested in.

For example:

* `devices/device123/telemetry/env_sensor`
* `devices/server123/backup_result/backup_service`

A client subscribing to one of these topics can receive the latest retained message for that topic, followed by any new live messages published afterward. Historical messages are stored separately in TimescaleDB and can be queried when replay or catch-up is needed.

## Auto cleanup

The database should be able to be configured to either retain all data indefinitely or automatically delete messages older than a certain age (e.g., 30 days) to manage storage space. This can be implemented using TimescaleDB's built-in data retention policies or custom cleanup script.

## Setup & Deployment

This project uses Docker Compose to orchestrate the server side. 

### 1. Configure the Environment
First, configure your credentials by copying the `.env.example` file:
```bash
cp .env.example .env
```
Edit `.env` to set your desired MQTT passwords, database credentials, and REST API Key.

### 2. Start the Stack
To build and start the entire stack (Mosquitto Broker, TimescaleDB, Python Bridge, and HTTP API) simply run:
```bash
docker compose up -d --build
```

The system will start out using the resource limits defined in `docker-compose.yml` if you run up against them you can modify them. Once started, Mosquitto listens on `:1883` and the REST API listens on `:8000`. TimescaleDB is firewalled behind the Docker network since the clients don't need to access it directly.

## How to use (Examples)

The `examples/` directory contains Python scripts showing how to talk to both the real-time MQTT broker and the HTTP Historical API.

First, install the example dependencies:
```bash
pip install paho-mqtt
```

### Publishing Messages
When a given device or service wants to register information, it connects to MQTT and publishes its JSON:
```bash
# This will constantly publish sample messages to topics
python examples/publisher.py
```

You can also publish updates over HTTP with `curl`, which is handy for bash scripts. The API will forward the message to MQTT (so live subscribers receive it) and the bridge will store it in TimescaleDB.
See [examples/publish.sh](examples/publish.sh) for curl-based publish examples.

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
