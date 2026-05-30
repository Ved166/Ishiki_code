import json

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from models import Activity, AnalysisHistory, Module, ModuleProgress, Result, UserBadge

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    completed = ModuleProgress.query.filter_by(
        user_id=current_user.id, completed=True
    ).count()
    total_modules = Module.query.count()
    results = Result.query.filter_by(user_id=current_user.id).order_by(
        Result.completed_at.desc()
    ).limit(5).all()
    badges = (
        UserBadge.query.filter_by(user_id=current_user.id)
        .order_by(UserBadge.earned_at.desc())
        .all()
    )
    analyses = (
        AnalysisHistory.query.filter_by(user_id=current_user.id)
        .order_by(AnalysisHistory.created_at.desc())
        .limit(8)
        .all()
    )
    activities = (
        Activity.query.filter_by(user_id=current_user.id)
        .order_by(Activity.created_at.desc())
        .limit(10)
        .all()
    )

    quiz_labels = []
    quiz_scores = []
    for r in reversed(results):
        quiz_labels.append(r.quiz.title[:20] if r.quiz else f"Quiz {r.quiz_id}")
        quiz_scores.append(round((r.score / r.total) * 100) if r.total else 0)

    risk_labels = ["Safe", "Suspicious", "High-Risk"]
    risk_counts = [0, 0, 0]
    for a in analyses:
        c = a.classification
        if "Safe" in c:
            risk_counts[0] += 1
        elif "Suspicious" in c:
            risk_counts[1] += 1
        else:
            risk_counts[2] += 1

    return render_template(
        "dashboard.html",
        completed=completed,
        total_modules=total_modules,
        results=results,
        badges=badges,
        analyses=analyses,
        activities=activities,
        quiz_labels=json.dumps(quiz_labels),
        quiz_scores=json.dumps(quiz_scores),
        risk_labels=json.dumps(risk_labels),
        risk_counts=json.dumps(risk_counts),
    )


@dashboard_bp.route("/leaderboard")
def leaderboard():
    users = User.query.order_by(User.xp.desc()).limit(20).all()
    return render_template("leaderboard.html", users=users)
