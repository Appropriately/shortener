#!/user/bin/env python
import click

from app import create_app, db, models, forms

app = create_app()


@app.shell_context_processor
def get_context():
    """Objects exposed here will be automatically available from the shell."""
    return dict(app=app, db=db, models=models, forms=forms)


@app.cli.command()
def create_db():
    """Create the configured database."""
    db.create_all()


@app.cli.command()
@click.confirmation_option(prompt='Drop all database tables?')
def drop_db():
    """Drop the current database."""
    db.drop_all()


@app.cli.command()
@click.argument('username')
@click.argument('email')
@click.argument('password')
def create_admin_user(username: str, email: str, password: str):
    """Create an admin. Requires a username, email, and password."""
    try:
        user = models.User(username=username, email=email, password=password)
        user.is_admin = True
        user.save()
    except Exception as e:
        print('There was an issue creating the user: ' + str(e))


if __name__ == '__main__':
    app.run()
