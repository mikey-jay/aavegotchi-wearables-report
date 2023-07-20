import datetime

def get_readable_time_from_timestamp(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

def get_readable_date_from_timestamp(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp).strftime('%d %b %Y')