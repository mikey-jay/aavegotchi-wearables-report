FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y cron lighttpd certbot openssl
RUN touch /var/log/cron.log
RUN chmod 0644 wearables_crontab
RUN crontab wearables_crontab

# Create the directory for Certbot verification files and set ownership
RUN mkdir /var/www/letsencrypt && \
    chown www-data:www-data /var/www/letsencrypt

# Obtain SSL certificate using Certbot, or create a self-signed certificate if that fails
RUN certbot certonly --agree-tos --register-unsafely-without-email --webroot -w /var/www/letsencrypt -d wearables.report --cert-path /etc/lighttpd/fullchain.pem --key-path /etc/lighttpd/privkey.pem || \
    openssl req -x509 -newkey rsa:4096 -keyout /etc/lighttpd/privkey.pem -out /etc/lighttpd/fullchain.pem -days 365 -nodes -subj "/CN=wearables.report"

EXPOSE 80
EXPOSE 443

CMD /etc/init.d/cron start && python main.py & lighttpd -D -f lighttpd.conf