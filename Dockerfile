FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y cron
RUN touch /var/log/cron.log
RUN chmod 0644 wearables_crontab
RUN crontab wearables_crontab

EXPOSE 80

CMD /etc/init.d/cron start && tail -f /var/log/cron.log & bin/update_wearables_dashboard & python -m http.server 80 --directory public