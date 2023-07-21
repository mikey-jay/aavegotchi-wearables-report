FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y cron && apt-get install -y lighttpd
RUN touch /var/log/cron.log
RUN chmod 0644 wearables_crontab
RUN crontab wearables_crontab

EXPOSE 80

CMD /etc/init.d/cron start && python main.py & lighttpd -D -f lighthttpd.conf