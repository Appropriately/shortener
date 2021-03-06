from flask import (
    Blueprint, current_app, render_template, request, flash, url_for, redirect
)
from flask_login import login_required, current_user
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root

from .forms import QuickLinkForm, LinkForm
from .models import Link
from .utils import get_dashboard_data, get_link_data

links_blueprint = Blueprint('links', __name__)
default_breadcrumb_root(links_blueprint, '.')


@links_blueprint.route('/link/new', methods=['GET', 'POST'])
@register_breadcrumb(links_blueprint, '.dashboard.new', 'New Link')
def new():
    form = LinkForm(request.form)
    if form.validate_on_submit():
        link = Link(user_id=current_user.id)
        form.populate_obj(link)
        link.save()

        flash(f'The link \'{link.link}\' was created.', 'success')
        return redirect(url_for('links.link', value=link.id))
    elif form.is_submitted():
        flash('There was a problem with the form submission.', 'danger')

    return render_template('links/new.html', form=form)


@links_blueprint.route('/link/<int:value>', methods=['GET', 'POST'])
@register_breadcrumb(links_blueprint, '.dashboard.value', 'Link')
def link(value: int):
    link = Link.find_by_id(value).first()

    if not link:
        flash(f'A link with the id \'{ value }\' does not exist.', 'danger')
        return redirect(url_for('links.dashboard'))

    form = LinkForm(obj=link)
    if form.validate_on_submit():
        form.populate_obj(link)
        link.update()

        flash(f'The link \'{link.link}\' was updated.', 'success')
    elif form.is_submitted():
        flash('The given URL was invalid.', 'danger')

    data = get_link_data(link.id)
    return render_template('links/link.html', form=form, link=link, data=data)


@links_blueprint.route('/dashboard', methods=['GET', 'POST'])
@register_breadcrumb(links_blueprint, '.dashboard', 'Dashboard')
def dashboard():
    form = QuickLinkForm(request.form)
    if form.validate_on_submit():
        link = Link(
            link=Link.unique_link(), redirect=form.redirect.data,
            user_id=current_user.id)
        link.save()

        flash(f'Url \'{ link.full_link() }\' was generated.', 'success')
        return redirect(url_for('links.link', value=link.id))
    elif form.is_submitted():
        flash('The given URL was invalid.', 'danger')

    try:
        dashboard_data = get_dashboard_data()
    except Exception as e:
        current_app.logger.warning(f'There was a problem: {e}. Hiding graphs.')
        dashboard_data = None

    links = current_user.links()
    return render_template(
        'links/dashboard.html', form=form, links=links, data=dashboard_data)


@links_blueprint.before_request
@login_required
def before_request():
    """Function performed before any request related to this breadcrumb.
    Stops the user from continuing if they aren't currently authenticated.
    """
    pass
