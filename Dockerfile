FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y cron lighttpd certbot openssl
RUN touch /var/log/cron.log
RUN chmod 0644 conf/crontab
RUN crontab conf/crontab

EXPOSE 80
EXPOSE 443

RUN chmod +x bin/start.sh
CMD bin/start.sh