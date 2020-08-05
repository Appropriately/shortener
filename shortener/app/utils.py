from . import db


class ModelMixin(object):
    """Additional functionality that is relevant to multiple sqlalchemy models.
    """

    def save(self):
        """Performs a save operation on the object.

        Returns:
            Object: an instance of the saved object.
        """
        db.session.add(self)
        db.session.commit()
        return self
