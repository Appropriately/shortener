from datetime import datetime

from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db, models
from ..utils import ModelMixin


class User(db.Model, UserMixin, ModelMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    activated = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    @hybrid_property
    def password(self) -> str:
        return self.password_hash

    @password.setter
    def password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def links(self) -> list:
        """[summary]

        Returns:
            list: [description]
        """
        if self.is_admin:
            query = models.Link.query
        else:
            query = models.Link.find_by_user_id(self.id)

        return query.order_by(models.Link.activated.desc()).all()

    @classmethod
    def authenticate(cls, user_id, password):
        user = cls.query \
            .filter(db.or_(cls.username == user_id, cls.email == user_id)) \
            .first()
        if user is not None and check_password_hash(user.password, password):
            return user

    def __str__(self) -> str:
        return '<User: %s>' % self.username


class AnonymousUser(AnonymousUserMixin):
    pass
