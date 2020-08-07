from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root

from .forms import QuickLinkForm
from .models import Link

links_blueprint = Blueprint('links', __name__)
default_breadcrumb_root(links_blueprint, '.')


@links_blueprint.route('/link/<int:value>', methods=['GET', 'POST'])
@register_breadcrumb(links_blueprint, '.dashboard.value', 'Link')
def link(value: int):
    link = Link.find_by_id(value).first()
    return render_template('links/link.html', link=link)


@links_blueprint.route('/dashboard', methods=['GET', 'POST'])
@login_required
@register_breadcrumb(links_blueprint, '.dashboard', 'Dashboard')
def dashboard():
    form = QuickLinkForm(request.form)
    if form.validate_on_submit():
        link = Link(link=Link.unique_link(), redirect=form.redirect.data)
        link.save()

        flash(f"Url '{ link.full_link() }' was generated.", 'success')
        return redirect(url_for('links.link', value=link.id), code=307)
    elif form.is_submitted():
        flash('The given URL was invalid.', 'danger')

    links = Link.query.all()[:5]
    return render_template('links/dashboard.html', form=form, links=links)
