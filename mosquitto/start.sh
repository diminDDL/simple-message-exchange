#!/bin/sh
set -e

# Generate the password file using environment variables from .env
if [ -n "$MQTT_USER" ] && [ -n "$MQTT_PASSWORD" ]; then
    touch /mosquitto/config/mosquitto.passwd
    mosquitto_passwd -b /mosquitto/config/mosquitto.passwd "$MQTT_USER" "$MQTT_PASSWORD"
    chown mosquitto:mosquitto /mosquitto/config/mosquitto.passwd
fi

# Execute the default mosquitto process
exec /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf