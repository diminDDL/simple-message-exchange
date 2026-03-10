CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS messages (
    time TIMESTAMPTZ NOT NULL,
    message_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    message_type TEXT NOT NULL,
    service_name TEXT NOT NULL,
    topic TEXT NOT NULL,
    payload JSONB NOT NULL
);

-- Turn into hypertable
SELECT create_hypertable('messages', 'time');

-- Data retention policy (30 days cleanup)
SELECT add_retention_policy('messages', INTERVAL '30 days');