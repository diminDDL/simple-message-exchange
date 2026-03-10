FROM eclipse-mosquitto:2

COPY mosquitto.conf /mosquitto/config/mosquitto.conf
COPY start.sh /mosquitto/start.sh

RUN chmod +x /mosquitto/start.sh && \
    chown -R mosquitto:mosquitto /mosquitto/config

CMD ["/mosquitto/start.sh"]