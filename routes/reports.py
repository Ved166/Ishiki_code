from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Report
from services.gamification import award_xp, log_activity

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/", methods=["GET", "POST"])
@login_required
def submit_report():
    if request.method == "POST":
        report_type = request.form.get("report_type", "").strip()
        description = request.form.get("description", "").strip()
        if not report_type or not description:
            flash("Please fill in all fields.", "danger")
        elif len(description) < 20:
            flash("Description must be at least 20 characters.", "danger")
        else:
            report = Report(
                user_id=current_user.id,
                report_type=report_type,
                description=description,
            )
            db.session.add(report)
            award_xp(current_user, 25, "Incident report submitted")
            log_activity(current_user.id, "Report submitted", report_type)
            db.session.commit()
            flash("Report submitted successfully. Thank you!", "success")
            return redirect(url_for("reports.my_reports"))
    return render_template("reports/submit.html")


@reports_bp.route("/my-reports")
@login_required
def my_reports():
    reports = Report.query.filter_by(user_id=current_user.id).order_by(
        Report.created_at.desc()
    ).all()
    return render_template("reports/my_reports.html", reports=reports)
