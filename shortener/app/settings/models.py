from enum import Enum, unique

from flask import current_app

from dateutil import parser

from .. import db
from ..utils import ModelMixin


@unique
class Type(Enum):
    """[summary]
    """
    STRING = 0
    BOOLEAN = 1
    INTEGER = 2
    FLOAT = 3
    DATETIME = 4


class Setting(db.Model, ModelMixin):
    """[summary]
    """
    __tablename__ = 'setting'

    id = db.Column(db.Integer, primary_key=True)
    value_type = db.Column(db.Integer, default=Type.STRING)
    key = db.Column(db.String, nullable=False)
    value = db.Column(db.String(500))

    @staticmethod
    def find_by_key(key: str) -> Setting:
        """[summary]

        Args:
            key (str): [description]

        Returns:
            Setting: [description]
        """
        return Setting.query.filter(Setting.key == key)

    @staticmethod
    def value_by_key(key: str):
        """[summary]

        Args:
            key (str): [description]

        Returns:
            [description]
        """
        try:
            setting = Setting.find_by_key(key)

            if setting.value_type is Type.BOOLEAN:
                return True if setting.value == 'True' else 'False'
            elif setting.value_type is Type.Integer:
                return int(setting.value)
            elif setting.value_type is Type.DECIMAl:
                return float(setting.value)
            elif setting.value_type is Type.DATETIME:
                return parser(setting.value)
            else:
                return setting.value
        except Exception as exception:
            current_app.logger \
                .error(f'Error with \'{key}\', returning None: {exception}')

        return None
