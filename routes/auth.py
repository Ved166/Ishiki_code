import secrets

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from extensions import bcrypt, db
from models import User
from services.gamification import log_activity, update_streak

auth_bp = Blueprint("auth", __name__)


def _validate_registration(username, email, password, confirm):
    errors = []
    if not username or len(username) < 3:
        errors.append("Username must be at least 3 characters.")
    if not email or "@" not in email:
        errors.append("Valid email is required.")
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters.")
    if password != confirm:
        errors.append("Passwords do not match.")
    if User.query.filter_by(username=username).first():
        errors.append("Username already taken.")
    if User.query.filter_by(email=email).first():
        errors.append("Email already registered.")
    return errors


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        errors = _validate_registration(username, email, password, confirm)
        if errors:
            for e in errors:
                flash(e, "danger")
        else:
            user = User(
                username=username,
                email=email,
                password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            )
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=bool(request.form.get("remember")))
            update_streak(user)
            log_activity(user.id, "Logged in")
            db.session.commit()
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))
        flash("Invalid username or password.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            db.session.commit()
            flash(
                f"Reset link generated (demo): /auth/reset-password/{token}",
                "info",
            )
        else:
            flash("If that email exists, a reset link has been sent.", "info")
    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash("Invalid or expired reset token.", "danger")
        return redirect(url_for("auth.forgot_password"))
    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
        elif password != confirm:
            flash("Passwords do not match.", "danger")
        else:
            user.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
            user.reset_token = None
            db.session.commit()
            flash("Password updated. Please log in.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html")


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if email and email != current_user.email:
            if User.query.filter(User.email == email, User.id != current_user.id).first():
                flash("Email already in use.", "danger")
            else:
                current_user.email = email
                db.session.commit()
                flash("Profile updated.", "success")
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        if new_password:
            if bcrypt.check_password_hash(current_user.password_hash, current_password):
                if len(new_password) >= 6:
                    current_user.password_hash = bcrypt.generate_password_hash(
                        new_password
                    ).decode("utf-8")
                    db.session.commit()
                    flash("Password changed.", "success")
                else:
                    flash("New password must be at least 6 characters.", "danger")
            else:
                flash("Current password is incorrect.", "danger")
    return render_template("auth/profile.html")
