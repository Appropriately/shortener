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

    count = 0
    by_browser = {}
    by_version = {}
    for request in requests:
        browser = request.user_agent['browser'].capitalize()
        version = request.user_agent['version'].split('.')[0]

        if browser:
            count += 1
            __increment_dict(browser, by_browser)
            __increment_dict(f'{browser} {version}', by_version)

    # Convert by_browser to percentage and split into keys/values.
    for key in by_browser.keys():
        by_browser[key] = by_browser[key] / count * 100

    labels, values = zip(*by_browser.items())
    data['browser'] = {'labels': labels, 'values': values}

    # Convert by_version to percentage, sort, and split into keys/values.
    for key in by_version.keys():
        by_version[key] = by_version[key] / count * 100

    filtered = sorted(by_version.items(), key=lambda x: x[1], reverse=True)[:5]
    labels, values = zip(*{k: v for k, v in filtered}.items())
    data['version'] = {'labels': labels, 'values': values}

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
    bots_week = {}
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
        if week not in bots_week:
            bots_week[week] = 0
        __increment_dict(week, hits_week if request.is_hit else misses_week)
        if request.is_bot:
            __increment_dict(week, bots_week)

    labels, values = zip(*requests_by_date.items())
    data['requests'] = {'labels': labels, 'values': values}

    hit_labels, hit_values = zip(*hits_week.items())
    misses_labels, misses_values = zip(*misses_week.items())
    bots_labels, bots_values = zip(*bots_week.items())
    data['hits'] = {
        'labels': list(hit_labels), 'misses': list(misses_values),
        'hits': list(hit_values), 'bots': list(bots_values)
    }

    return data
