from datetime import datetime, timedelta

from .models import Request


def __increment_dict(key: str, dictionary: dict):
    """A helper function that iterates a value in a dictionary. If the key does
    not exists, then the key is added with the value '1'.

    Args:
        key (str): the particular key to increment.
        dictionary (dict): the dictionary that requires incrementing.
    """
    if key in dictionary:
        dictionary[key] += 1
    else:
        dictionary[key] = 1


def get_dashboard_data() -> dict:
    """Generate dashboard data, that can be used for graph information.
    Currently interprets only the request data from the past 5 weeks.

    Returns:
        dict: a dictionary of data that can be fed to chart.js.
    """
    data = {}
    today = datetime.now()

    requests = Request.query \
        .filter(Request.end > (today - timedelta(weeks=5))) \
        .order_by(Request.end.asc()) \
        .all()

    requests_by_date = {}
    hits_week = {}
    misses_week = {}
    for request in requests:
        if request.is_hit and request.end > (today - timedelta(weeks=1)):
            date = request.end.strftime('%x')
            __increment_dict(date, requests_by_date)

        week = request.end.strftime('Week %W, %Y')
        if week not in hits_week:
            hits_week[week] = 0
        if week not in misses_week:
            misses_week[week] = 0
        __increment_dict(week, hits_week if request.is_hit else misses_week)

    labels, values = zip(*requests_by_date.items())
    data['requests'] = {'labels': labels, 'values': values}

    hit_labels, hit_values = zip(*hits_week.items())
    misses_labels, misses_values = zip(*misses_week.items())
    data['hits'] = {
        'labels': list(hit_labels),
        'hits': list(hit_values), 'misses': list(misses_values)
    }

    return data
