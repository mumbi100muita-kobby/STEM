"""SQLAlchemy models.

Importing this package registers models with Flask-Migrate's metadata.
"""

from stem.models.user import User

__all__ = ["User"]
