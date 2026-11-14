from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

from stem.blueprints.auth import routes  # noqa: E402,F401
