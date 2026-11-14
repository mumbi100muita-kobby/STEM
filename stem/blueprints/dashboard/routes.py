"""Student dashboard HTTP handlers. Protected with Flask-Login."""

from flask import redirect, render_template, url_for
from flask_login import current_user, login_required

from stem.blueprints.dashboard import dashboard_bp


@dashboard_bp.route("/")
def home():
    """Send visitors to the dashboard or the login page."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))


@dashboard_bp.route("/dashboard")
@login_required
def index():
    return render_template("dashboard/index.html")
