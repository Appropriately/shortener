import os
import sass

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_breadcrumbs import Breadcrumbs
from logging.config import dictConfig
from werkzeug.exceptions import HTTPException

# instantiate extensions
login_manager = LoginManager()
db = SQLAlchemy()


def create_app(environment='development'):
    from config import config
    from .views import main_blueprint
    from .auth.views import auth_blueprint
    from .settings.views import settings_blueprint
    from .links.views import links_blueprint
    from .auth.models import User, AnonymousUser

    # Setup configuration
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    # Instantiate app.
    app = Flask(__name__)
    with app.app_context():
        from .filters import humanize_number # noqa

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
    app.register_blueprint(settings_blueprint)
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
    def handle_http_error(exc):
        return render_template('error.html', error=exc), exc.code

    return app
