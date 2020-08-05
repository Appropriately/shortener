from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, ValidationError
from wtforms.validators import DataRequired, URL

from .models import Link


class QuickLinkForm(FlaskForm):
    redirect = StringField('URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Generate')


class LinkForm(FlaskForm):
    link = StringField('URL', validators=[URL()])
    redirect = StringField('URL', validators=[DataRequired(), URL()])
    expiration = DateField('Expiration date')
    submit = SubmitField('Generate')

    def validate_link(self, field):
        if Link.active_links_with_value(field).first():
            raise ValidationError('This link is already in use.')
