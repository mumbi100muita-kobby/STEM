"""Auth HTTP handlers: parse forms, call auth_service, manage the session."""

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from stem.blueprints.auth import auth_bp
from stem.blueprints.auth.forms import LoginForm, RegisterForm
from stem.services.auth_service import AuthError, authenticate_user, register_user


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = register_user(form.email.data, form.password.data)
        except AuthError as exc:
            form_field = getattr(form, exc.field, None) if exc.field else None
            if form_field is not None:
                form_field.errors.append(exc.message)
            else:
                flash(exc.message, "danger")
            return render_template("auth/register.html", form=form)

        login_user(user)
        flash("Welcome to S.T.E.M. Your account is ready.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = authenticate_user(form.email.data, form.password.data)
        except AuthError as exc:
            flash(exc.message, "danger")
            return render_template("auth/login.html", form=form)

        login_user(user)
        flash("You are logged in.", "success")
        next_url = request.args.get("next")
        if next_url and next_url.startswith("/") and not next_url.startswith("//"):
            return redirect(next_url)
        return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
