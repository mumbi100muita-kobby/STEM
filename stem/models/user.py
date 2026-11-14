"""Student account persisted in the users table."""

from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from stem.extensions import db, login_manager


class User(UserMixin, db.Model):
    """A registered student.

    Passwords are stored only as a Werkzeug hash in password_hash.
    The plaintext password is never written to the database.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def set_password(self, plaintext_password):
        """Hash and store a password using Werkzeug's default algorithm."""
        self.password_hash = generate_password_hash(plaintext_password)

    def check_password(self, plaintext_password):
        """Return True if the given password matches the stored hash."""
        return check_password_hash(self.password_hash, plaintext_password)

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id):
    """Reload the logged-in student from the session user id."""
    if not user_id:
        return None
    return db.session.get(User, int(user_id))
