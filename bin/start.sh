#!/bin/bash

# Start Lighttpd without SSL support
echo "Starting Lighttpd without SSL support..."
lighttpd -D -f /usr/src/app/conf/lighttpd.conf &

# Wait for Lighttpd to start
sleep 5

# Obtain SSL certificate using Certbot, or create a self-signed certificate if that fails
echo "Obtaining SSL certificate using Certbot..."
if certbot certonly --agree-tos --register-unsafely-without-email --webroot -w /usr/src/app/public -d wearables.report; then
  echo "Copying SSL certificate files..."
  cp /etc/letsencrypt/live/wearables.report/*.pem /etc/lighttpd/
else
  echo "Certbot failed, creating self-signed certificate..."
  openssl req -x509 -newkey rsa:4096 -keyout /etc/lighttpd/privkey.pem -out /etc/lighttpd/fullchain.pem -days 365 -nodes -subj "/CN=wearables.report"
fi

# Stop the original instance of Lighttpd
echo "Stopping the original instance of Lighttpd..."
pkill lighttpd

# Start cron
echo "Starting cron..."
/etc/init.d/cron start

# Start the Python application
echo "Starting the Python application..."
python main.py

# Start Lighttpd with SSL support
echo "Starting Lighttpd with SSL support..."
lighttpd -D -f /usr/src/app/conf/lighttpd.ssl.conf