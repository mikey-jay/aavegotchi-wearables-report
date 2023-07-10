import datetime
import calendar
import time
import math

def get_midnight_utc_today():
    utc_now_struct = time.gmtime()
    return int(calendar.timegm(datetime.datetime(utc_now_struct.tm_year, utc_now_struct.tm_mon, utc_now_struct.tm_mday, 0, 0, 0, 0, datetime.timezone.utc).timetuple()))

def get_first_of_month_utc(unix_time):
    utc_struct = time.gmtime(unix_time)
    return int(calendar.timegm(datetime.datetime(utc_struct.tm_year, utc_struct.tm_mon, 1, 0, 0, 0, 0, datetime.timezone.utc).timetuple()))

def round_time_to_nearest_minutes(minutes=1, precise_time=time.time()):
    return math.floor(precise_time / (60 * minutes)) * (60 * minutes)

def days_ago(days):
    return round(time.time() - (days * 24 * 60 * 60))

def get_first_day_of_week(d):
    weekday = d.isocalendar().weekday - 1
    return d - datetime.timedelta(days=weekday)

def get_time_intervals(start, end, step):
    while start <= end:
        yield start
        start += step