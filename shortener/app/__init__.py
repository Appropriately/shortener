import os
import sass

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_breadcrumbs import Breadcrumbs, register_breadcrumb
from werkzeug.exceptions import HTTPException

# instantiate extensions
login_manager = LoginManager()
db = SQLAlchemy()


def create_app(environment='development'):
    from config import config
    from .views import main_blueprint
    from .auth.views import auth_blueprint
    from .links.views import links_blueprint
    from .auth.models import User, AnonymousUser

    # Instantiate app.
    app = Flask(__name__)

    # Compile the SASS
    dirname = ('app/static/sass', 'app/static/css')
    sass.compile(dirname=dirname, output_style='compressed')

    # Initialise the breadcrumb system.
    Breadcrumbs(app=app)

    # Set app config.
    env = os.environ.get('FLASK_ENV', environment)
    app.config.from_object(config[env])
    config[env].configure(app)

    # Set up extensions.
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints.
    app.register_blueprint(links_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)

    # Set up flask login.
    @login_manager.user_loader
    def get_user(id):
        return User.query.get(int(id))

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.anonymous_user = AnonymousUser

    # Error handlers.
    @app.errorhandler(HTTPException)
    @register_breadcrumb(app, '.error', 'Error')
    def handle_http_error(exc):
        return render_template('error.html', error=exc), exc.code

    return app
