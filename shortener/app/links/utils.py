from datetime import datetime, timedelta

from .models import Request, Link


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


def get_link_data(link_id: int) -> dict:
    """Generate dashboard data, that can be used for graph information.

    Args:
        link_id (int): an id for a particular instance of a link.

    Returns:
        dict: a dictionary of data that can be fed to chart.js.
    """
    data = {}

    requests = Request.find_by_link(link_id).order_by(Request.end.asc()).all()

    if not requests:
        return None

    browser_count = 0
    request_by_browser = {}
    for request in requests:
        browser = request.user_agent['browser'].capitalize()
        if browser:
            browser_count += 1
            __increment_dict(browser, request_by_browser)

    for key in request_by_browser.keys():
        request_by_browser[key] = request_by_browser[key] / browser_count * 100

    labels, values = zip(*request_by_browser.items())
    data['browser'] = {'labels': labels, 'values': values}

    return data


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

    if not requests:
        return None

    requests_by_date = {}
    hits_week = {}
    misses_week = {}
    link_ids = [link.id for link in Link.find_by_current_user()]
    for request in requests:
        in_range = request.end > (today - timedelta(weeks=1))
        if request.is_hit and in_range and request.link_id in link_ids:
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
