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

    def update(self):
        """Commits changes to the current object, without adding it to the
        session.

        Returns:
            Object: an instance of the saved object.
        """
        db.session.commit()
        return self

    def delete(self):
        """Performs a delete operation on the appropriate database row.

        Returns:
            Object: an instance of the deleted object.
        """
        db.session.delete(self)
        db.session.commit()
        return self
