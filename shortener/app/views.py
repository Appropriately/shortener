from datetime import datetime

from flask import render_template, Blueprint, request, redirect
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root

from .models import Request, Link

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

    model.end = datetime.now()
    model.save()

    if link:
        return redirect(link.redirect, code=302)
    else:
        return render_template('link.html', request=model)
