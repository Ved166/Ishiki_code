import json
from datetime import date

from extensions import db
from models import Activity, AnalysisHistory, Badge, ModuleProgress, Result, SimulationAttempt, User, UserBadge


BADGE_DEFINITIONS = [
    ("Beginner Defender", "Complete your first learning module", 0, "first_module"),
    ("Email Detective", "Analyze 5 emails", 0, "email_analyses_5"),
    ("URL Inspector", "Analyze 5 URLs", 0, "url_analyses_5"),
    ("Cyber Guardian", "Earn 500 XP", 500, "xp_500"),
    ("Quiz Master", "Pass 3 quizzes with 80%+", 0, "quiz_master"),
    ("Simulation Expert", "Get 10 simulation answers correct", 0, "sim_expert"),
]


def log_activity(user_id: int, action: str, details: str = None):
    db.session.add(Activity(user_id=user_id, action=action, details=details))


def award_xp(user: User, amount: int, reason: str):
    user.xp = (user.xp or 0) + amount
    log_activity(user.id, "XP earned", f"+{amount} — {reason}")
    _check_badges(user)


def update_streak(user: User):
    today = date.today()
    if user.last_activity_date == today:
        return
    if user.last_activity_date and (today - user.last_activity_date).days == 1:
        user.learning_streak = (user.learning_streak or 0) + 1
    else:
        user.learning_streak = 1
    user.last_activity_date = today


def save_analysis(user_id: int, analysis_type: str, preview: str, result):
    entry = AnalysisHistory(
        user_id=user_id,
        analysis_type=analysis_type,
        input_preview=preview[:500],
        risk_score=result.risk_score,
        classification=result.classification,
        details_json=json.dumps(
            [{"rule": r.rule_name, "explanation": r.explanation} for r in getattr(result, "triggered_rules", [])]
        ),
    )
    db.session.add(entry)
    return entry


def _user_has_badge(user_id: int, badge_name: str) -> bool:
    return (
        UserBadge.query.join(Badge)
        .filter(UserBadge.user_id == user_id, Badge.badge_name == badge_name)
        .first()
        is not None
    )


def _award_badge(user: User, badge_name: str):
    if _user_has_badge(user.id, badge_name):
        return
    badge = Badge.query.filter_by(badge_name=badge_name).first()
    if badge:
        db.session.add(UserBadge(user_id=user.id, badge_id=badge.id))
        log_activity(user.id, "Badge earned", badge_name)


def _check_badges(user: User):
    completed = ModuleProgress.query.filter_by(user_id=user.id, completed=True).count()
    if completed >= 1:
        _award_badge(user, "Beginner Defender")

    email_count = AnalysisHistory.query.filter_by(user_id=user.id, analysis_type="email").count()
    if email_count >= 5:
        _award_badge(user, "Email Detective")

    url_count = AnalysisHistory.query.filter_by(user_id=user.id, analysis_type="url").count()
    if url_count >= 5:
        _award_badge(user, "URL Inspector")

    if (user.xp or 0) >= 500:
        _award_badge(user, "Cyber Guardian")

    results = Result.query.filter_by(user_id=user.id).all()
    passed = sum(1 for r in results if r.total and (r.score / r.total) >= 0.8)
    if passed >= 3:
        _award_badge(user, "Quiz Master")

    correct_sims = SimulationAttempt.query.filter_by(user_id=user.id, correct=True).count()
    if correct_sims >= 10:
        _award_badge(user, "Simulation Expert")


def ensure_badges_exist():
    for name, desc, xp_req, criteria in BADGE_DEFINITIONS:
        if not Badge.query.filter_by(badge_name=name).first():
            db.session.add(
                Badge(badge_name=name, description=desc, xp_required=xp_req, criteria=criteria)
            )
    db.session.commit()
