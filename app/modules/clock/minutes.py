from datetime import datetime


def minutes(start, end):
    interval = datetime.fromisoformat(end) - datetime.fromisoformat(start)
    return interval.days * 1440 + interval.seconds // 60
