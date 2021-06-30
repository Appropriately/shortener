from .. import db
from ..utils import ModelMixin

from sqlalchemy import or_
from sqlalchemy.orm import validates
from flask import url_for
from flask_sqlalchemy import BaseQuery
from flask_login import current_user
from datetime import datetime, timedelta
from random import choice
from string import digits, ascii_letters
from urllib.parse import urlparse


class Link(db.Model, ModelMixin):
    """A particular link between the shorterned value and the redirect."""

    __tablename__ = 'links'
    __table_args__ = {'extend_existing': True}

    LINK_SIZE = 6
    VALID_CHARS = digits + ascii_letters + '-_'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    requests = db.relationship('Request', backref='links', lazy=True)
    link = db.Column(db.String, nullable=False)
    redirect = db.Column(db.String(500), nullable=False)
    activated = db.Column(db.Boolean, default=True)
    track_requests = db.Column(db.Boolean, default=True)
    expiration = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)

    @validates('link')
    def validate_link(self, key: str, link: str) -> str:
        """Perform validation on a link, ensuring that it is the only
        allowed if there are no other similar links validated.

        Args:
            key (str): will always be 'link' in this context.
            link (str): the link that needs validation.

        Raises:
            AssertionError: raised if the link is already in use, or contains
                illegal characters.

        Returns:
            str: the link that just had validation performed.
        """
        if Link.active_with_link(link).filter(Link.id != self.id).first():
            raise AssertionError(f'The link { link } is already in use')

        if not all(char in Link.VALID_CHARS for char in link):
            raise AssertionError('The link contains invalid characters')

        return link

    def requests_for_today(self) -> list:
        """Returns all requests that have been performed today.

        Returns:
            list: a list of requests objects which ended in the day today.
        """
        today = datetime.now().date()
        return list(filter(lambda x: x.end.date() == today, self.requests))

    def is_expired(self) -> bool:
        return self.expiration and datetime.now() >= self.expiration

    def is_active(self) -> bool:
        return self.activated and not self.is_expired()

    def short_redirect(self) -> str:
        """The domain information for the redirect. Useful for quickly
        referencing a redirect.

        Returns:
            str: the domain for the redirect.
        """
        parsed = urlparse(self.redirect)
        return parsed.netloc

    def full_link(self) -> str:
        """Returns the full, external link to the redirect; includes domain and
        port information.

        Returns:
            str: url for current link.
        """
        return url_for('main.link', route=self.link, _external=True)

    def __str__(self) -> str:
        return f'<Link: { self.link } -> { self.redirect }>'

    @staticmethod
    def find_by_user_id(id: int) -> BaseQuery:
        """Get all links for the user with the given id.

        Args:
            id (int): the id of a particular user.

        Returns:
            BaseQuery: results of the performed query.
        """
        return Link.query.filter(Link.user_id == id)

    @staticmethod
    def find_by_current_user() -> BaseQuery:
        """Get all links for the current user.

        Returns:
            BaseQuery: results of the performed query.
        """
        return Link.find_by_user_id(current_user.id)

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
    def active() -> BaseQuery:
        """Returns an SQLAlchemy query, with only active links returned.

        Returns:
            BaseQuery: a query instance that can include further filters.
        """
        return Link.query.filter(Link.activated)

    @staticmethod
    def active_with_link(route: str, include_expiration=False) -> BaseQuery:
        """Returns an SQLAlchemy query of all active links with a particular
        route value. Includes the option to look for expired links.

        Args:
            route (str): a particular link to search for.
            include_expiration (bool, optional): whether the query should
                include expired links. Defaults to False.

        Returns:
            BaseQuery: a query instance that can include further filters.
        """
        query = Link.active().filter(Link.link == route)

        if include_expiration:
            check = Link.expiration.is_(None), Link.expiration > datetime.now()
            query = query.filter(or_(*check))

        return query

    @staticmethod
    def unique_link() -> str:
        """Generates a unique, random alphanumeric link value of size
        Link.LINK_SIZE.

        Returns:
            str: a randomly generated, unique link value.
        """
        list = (choice(Link.VALID_CHARS) for _ in range(Link.LINK_SIZE))
        value = ''.join(list)

        while Link.active_with_link(value, include_expiration=True).first():
            list = (choice(Link.VALID_CHARS) for _ in range(Link.LINK_SIZE))
            value = ''.join(list)

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
    is_bot = db.Column(db.Boolean, default=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    user_agent = db.Column(db.PickleType)

    def __str__(self) -> str:
        return f'<Request: { self._link }, is_hit = { self.is_hit }>'

    def duration(self) -> timedelta:
        """Returns the difference between the end and start time, as a
        timedelta value.

        Returns:
            timedelta: difference between end and start time.
        """
        return self.end - self.start

    @staticmethod
    def find_by_link(id: int) -> BaseQuery:
        """Finds all requests with a particular link_id.

        Args:
            id (int): the link's ID.

        Returns:
            BaseQuery: results of the performed query.
        """
        return Request.query.filter(Request.link_id == id)

    @staticmethod
    def hit() -> BaseQuery:
        return Request.query.filter(Request.is_hit)
