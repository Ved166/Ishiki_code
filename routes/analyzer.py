import os

from flask import Blueprint, current_app, flash, render_template, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from extensions import db
from services.email_analyzer import analyze_email
from services.gamification import award_xp, save_analysis, update_streak
from services.social_engineering import analyze_social_engineering
from services.url_analyzer import analyze_url

analyzer_bp = Blueprint("analyzer", __name__)


@analyzer_bp.route("/email", methods=["GET", "POST"])
@login_required
def email_analyzer():
    result = None
    content = ""
    if request.method == "POST":
        content = request.form.get("email_content", "")
        if "email_file" in request.files:
            f = request.files["email_file"]
            if f and f.filename:
                if f.filename.endswith((".txt", ".eml", ".msg")):
                    content = f.read().decode("utf-8", errors="ignore")
                else:
                    flash("Upload .txt or .eml files only.", "warning")
        if content.strip():
            result = analyze_email(content)
            save_analysis(current_user.id, "email", content, result)
            update_streak(current_user)
            award_xp(current_user, 10, "Email analysis")
            db.session.commit()
        else:
            flash("Please paste or upload email content.", "warning")
    return render_template("analyzer/email.html", result=result, content=content)


@analyzer_bp.route("/url", methods=["GET", "POST"])
@login_required
def url_analyzer():
    result = None
    url_input = ""
    if request.method == "POST":
        url_input = request.form.get("url", "").strip()
        if url_input:
            result = analyze_url(url_input)
            save_analysis(current_user.id, "url", url_input, result)
            update_streak(current_user)
            award_xp(current_user, 10, "URL analysis")
            db.session.commit()
        else:
            flash("Please enter a URL.", "warning")
    return render_template("analyzer/url.html", result=result, url_input=url_input)


@analyzer_bp.route("/social", methods=["GET", "POST"])
@login_required
def social_detector():
    result = None
    text = ""
    if request.method == "POST":
        text = request.form.get("text", "")
        if text.strip():
            result = analyze_social_engineering(text)
            update_streak(current_user)
            award_xp(current_user, 5, "Social engineering analysis")
            db.session.commit()
        else:
            flash("Please enter text to analyze.", "warning")
    return render_template("analyzer/social.html", result=result, text=text)
