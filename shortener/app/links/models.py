from .. import db
from ..utils import ModelMixin

from sqlalchemy import and_
from sqlalchemy.orm import validates
from flask import url_for
from flask_sqlalchemy import BaseQuery
from datetime import datetime
from random import choice
from string import hexdigits
from urllib.parse import urlparse


class Link(db.Model, ModelMixin):
    """A particular link between the shorterned value and the redirect."""

    __tablename__ = 'links'
    __table_args__ = {'extend_existing': True}

    LINK_SIZE = 6

    id = db.Column(db.Integer, primary_key=True)
    requests = db.relationship('Request', backref='links', lazy=True)
    link = db.Column(db.String, nullable=False)
    redirect = db.Column(db.String(500), nullable=False)
    activated = db.Column(db.Boolean, default=True)
    expiration = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)

    @validates('link')
    def validate_link(self, key: str, value: str) -> str:
        """Perform validation on a link, ensuring that it is the only
        allowed if there are no other similar links validated.

        Args:
            key (str): will always be 'link' in this context.
            value (str): the value that needs validation.

        Raises:
            AssertionError: raised if the link is already in use.

        Returns:
            str: the value that just had validation performed.
        """
        if Link.active_links_with_value(value).first():
            raise AssertionError(f'The link { value } is already in use')

        return value

    def short_redirect(self) -> str:
        """The domain information for the redirect. Useful for quickly
        referencing a redirect.

        Returns:
            str: the domain for the redirect.
        """
        parsed = urlparse(self.redirect)
        return parsed.netloc

    def full_link(self) -> str:
        """Returns the full, external link; includes domain and port
        information.

        Returns:
            str: url for current link.
        """
        return url_for('main.link', route=self.link, _external=True)

    def __str__(self) -> str:
        return f'<Link: { self.link } -> { self.redirect }>'

    @staticmethod
    def find_by_id(field: int) -> BaseQuery:
        """Perform a query on the 'links' table, to find a value of Link with
        the given ID.

        Args:
            field (int): the link's ID.

        Returns:
            BaseQuery: results of the performed query.
        """
        return Link.query.filter(Link.id == field)

    @staticmethod
    def active_links_with_value(field) -> BaseQuery:
        return Link.query.filter(and_(Link.link == field, Link.activated))

    @staticmethod
    def unique_link() -> str:
        """Generates a unique, random alphanumeric link value of size
        Link.LINK_SIZE.

        Returns:
            str: a randomly generated, unique link value.
        """
        value = ''.join(choice(hexdigits) for _ in range(Link.LINK_SIZE))

        while Link.active_links_with_value(value).first():
            value = ''.join(choice(hexdigits) for _ in range(Link.LINK_SIZE))

        return value


class Request(db.Model, ModelMixin):
    """A particular request to a link, storing information relevant to the
    request.
    """

    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('links.id'), nullable=True)
    route = db.Column(db.String, nullable=False)
    is_hit = db.Column(db.Boolean, default=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    user_agent = db.Column(db.PickleType)

    def __str__(self) -> str:
        return f'<Request: { self._link }, is_hit = { self.is_hit }>'
