from flask import Blueprint, render_template, flash, url_for, redirect
from flask_login import login_required, current_user
from flask_breadcrumbs import register_breadcrumb, default_breadcrumb_root

settings_blueprint = Blueprint('settings', __name__, url_prefix='/settings')
default_breadcrumb_root(settings_blueprint, '.')


@settings_blueprint.route('/', methods=['GET'])
@register_breadcrumb(settings_blueprint, '.settings', 'Settings')
def index():
    return render_template('settings/index.html')


@settings_blueprint.before_request
@login_required
def before_request():
    """Function performed before any request related to this breadcrumb.
    Stops the user from continuing if they aren't currently authenticated.
    """
    if current_user.is_admin is False:
        flash('You need to be an admin to access this page.', 'danger')
        return redirect(url_for('main.index'))
