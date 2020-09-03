from datetime import datetime

from flask import current_app, render_template, Blueprint, request, redirect
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root

from .models import Request, Link
import re

main_blueprint = Blueprint('main', __name__)
default_breadcrumb_root(main_blueprint, '.')


@main_blueprint.route('/')
@register_breadcrumb(main_blueprint, '.', 'Home')
def index():
    return render_template('index.html')


@main_blueprint.route('/l/<string:route>')
@register_breadcrumb(main_blueprint, '.link', 'Missing Link')
def link(route: str):
    """Performs a check on the given route, determining whether an active link
    with that route exists. Collects data on the particular request. If an
    appropriate link exists, redirect to the appropriate url.

    Args:
        route (str): the route requested.
    """

    start_time = datetime.now()
    link = Link.active_with_link(route, include_expiration=True).first()

    model = Request(start=start_time, route=route)
    if link:
        model.is_hit = True
        model.link_id = link.id

    model.user_agent = vars(request.user_agent)

    user_agent_string = model.user_agent['string']
    # Pull extended information from the user agent string
    if user_agent_string[:11] == 'Mozilla/5.0':
        expression = re.compile(r'\(([\w\.\s]+);\s([\w\.\s]+)')
        match = expression.search(user_agent_string)

        model.user_agent['operating_system'] = {
            'name': match.group(1), 'version': match.group(2)
        }

    # Determine whether the request is from a bot or not
    is_bot = re.compile(r'/bot|crawler|spider|crawling/i')
    model.is_bot = user_agent_string and is_bot.search(user_agent_string)

    model.end = datetime.now()
    if not link or link.track_requests:
        model.save()

    current_app.logger.debug(f'Took { model.duration().microseconds / 1e6 }s')
    if link:
        current_app.logger.info(f"Performed redirect for link '{ link.id }'")
        return redirect(link.redirect, code=302)
    else:
        current_app.logger.info(f"Link with route '{ route }' does not exist")
        return render_template('link.html', request=model)
