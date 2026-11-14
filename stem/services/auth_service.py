"""Registration and authentication rules, independent of HTTP.

Blueprints collect form data and call these functions. Validation lives here
so Pytest can exercise it without going through templates.
"""

import re

from email_validator import EmailNotValidError, validate_email
from sqlalchemy.exc import IntegrityError

from stem.extensions import db
from stem.models.user import User

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


class AuthError(Exception):
    """Raised when registration or login input cannot be accepted."""

    def __init__(self, message, field=None):
        super().__init__(message)
        self.message = message
        self.field = field


def normalize_email(email):
    """Trim, lowercase, and validate an email address."""
    if email is None or not str(email).strip():
        raise AuthError("Email is required.", field="email")

    try:
        result = validate_email(str(email).strip(), check_deliverability=False)
    except EmailNotValidError as exc:
        raise AuthError("Enter a valid email address.", field="email") from exc

    return result.normalized.lower()


def validate_password(password):
    """Reject empty, too-short, too-long, or whitespace-only passwords."""
    if password is None:
        raise AuthError("Password is required.", field="password")

    if not isinstance(password, str):
        raise AuthError("Password is required.", field="password")

    if password != password.strip() or not password.strip():
        raise AuthError(
            "Password cannot start or end with whitespace.",
            field="password",
        )

    if len(password) < MIN_PASSWORD_LENGTH:
        raise AuthError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters.",
            field="password",
        )

    if len(password) > MAX_PASSWORD_LENGTH:
        raise AuthError(
            f"Password must be at most {MAX_PASSWORD_LENGTH} characters.",
            field="password",
        )

    if re.fullmatch(r"\s+", password):
        raise AuthError("Password cannot be only whitespace.", field="password")

    return password


def register_user(email, password):
    """Create a student with a unique email and a hashed password.

    Returns the new User. Raises AuthError for validation or uniqueness issues.
    """
    normalized_email = normalize_email(email)
    validate_password(password)

    existing = User.query.filter_by(email=normalized_email).first()
    if existing is not None:
        raise AuthError("An account with this email already exists.", field="email")

    user = User(email=normalized_email)
    user.set_password(password)
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise AuthError(
            "An account with this email already exists.",
            field="email",
        ) from exc

    return user


def authenticate_user(email, password):
    """Return the matching User or raise AuthError with a generic message.

    The message is intentionally the same for unknown emails and bad passwords
    so login pages do not reveal which accounts exist.
    """
    invalid = AuthError("Invalid email or password.")

    try:
        normalized_email = normalize_email(email)
    except AuthError as exc:
        raise invalid from exc

    if not password:
        raise invalid

    user = User.query.filter_by(email=normalized_email).first()
    if user is None or not user.check_password(password):
        raise invalid

    return user
