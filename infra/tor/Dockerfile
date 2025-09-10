FROM debian:stable-slim
RUN apt-get update && apt-get install -y --no-install-recommends tor ca-certificates && rm -rf /var/lib/apt/lists/*
COPY torrc /etc/tor/torrc
# tor пишет ключи/hostname сюда — даём владельца
RUN chown -R debian-tor:debian-tor /var/lib/tor
USER debian-tor
CMD ["tor", "-f", "/etc/tor/torrc"]