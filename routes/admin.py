from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import bcrypt, db
from models import (
    AnalysisHistory,
    Module,
    Question,
    Quiz,
    Report,
    Result,
    User,
)
from services.gamification import ensure_badges_exist

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@admin_required
def dashboard():
    total_users = User.query.count()
    total_reports = Report.query.count()
    pending_reports = Report.query.filter_by(status="pending").count()
    results = Result.query.all()
    avg_score = 0
    if results:
        avg_score = sum((r.score / r.total) * 100 for r in results if r.total) / len(results)

    analyses = AnalysisHistory.query.all()
    indicator_counts = {}
    for a in analyses:
        key = a.classification
        indicator_counts[key] = indicator_counts.get(key, 0) + 1

    recent_activity = AnalysisHistory.query.order_by(
        AnalysisHistory.created_at.desc()
    ).limit(10).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_reports=total_reports,
        pending_reports=pending_reports,
        avg_score=round(avg_score, 1),
        indicator_counts=indicator_counts,
        recent_activity=recent_activity,
    )


@admin_bp.route("/users")
@admin_required
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users_list)


@admin_bp.route("/users/add", methods=["GET", "POST"])
@admin_required
def add_user():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "user")
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email exists.", "danger")
        else:
            user = User(
                username=username,
                email=email,
                password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
                role=role,
            )
            db.session.add(user)
            db.session.commit()
            flash("User created.", "success")
            return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", user=None)


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        user.username = request.form.get("username", user.username).strip()
        user.email = request.form.get("email", user.email).strip()
        user.role = request.form.get("role", user.role)
        new_pass = request.form.get("password", "")
        if new_pass:
            user.password_hash = bcrypt.generate_password_hash(new_pass).decode("utf-8")
        db.session.commit()
        flash("User updated.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", user=user)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Cannot delete yourself.", "danger")
    else:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/modules")
@admin_required
def modules():
    modules_list = Module.query.order_by(Module.order_index).all()
    return render_template("admin/modules.html", modules=modules_list)


@admin_bp.route("/modules/add", methods=["GET", "POST"])
@admin_required
def add_module():
    if request.method == "POST":
        mod = Module(
            title=request.form.get("title"),
            description=request.form.get("description"),
            content=request.form.get("content"),
            order_index=int(request.form.get("order_index", 0)),
        )
        db.session.add(mod)
        db.session.commit()
        flash("Module added.", "success")
        return redirect(url_for("admin.modules"))
    return render_template("admin/module_form.html", module=None)


@admin_bp.route("/modules/<int:module_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_module(module_id):
    module = Module.query.get_or_404(module_id)
    if request.method == "POST":
        module.title = request.form.get("title")
        module.description = request.form.get("description")
        module.content = request.form.get("content")
        module.order_index = int(request.form.get("order_index", 0))
        db.session.commit()
        flash("Module updated.", "success")
        return redirect(url_for("admin.modules"))
    return render_template("admin/module_form.html", module=module)


@admin_bp.route("/modules/<int:module_id>/delete", methods=["POST"])
@admin_required
def delete_module(module_id):
    module = Module.query.get_or_404(module_id)
    db.session.delete(module)
    db.session.commit()
    flash("Module deleted.", "success")
    return redirect(url_for("admin.modules"))


@admin_bp.route("/quizzes")
@admin_required
def quizzes():
    quizzes_list = Quiz.query.all()
    return render_template("admin/quizzes.html", quizzes=quizzes_list)


@admin_bp.route("/quizzes/<int:quiz_id>/questions")
@admin_required
def quiz_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template("admin/questions.html", quiz=quiz, questions=questions)


@admin_bp.route("/quizzes/<int:quiz_id>/questions/add", methods=["GET", "POST"])
@admin_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == "POST":
        q = Question(
            quiz_id=quiz_id,
            question=request.form.get("question"),
            question_type=request.form.get("question_type", "multiple_choice"),
            option_a=request.form.get("option_a"),
            option_b=request.form.get("option_b"),
            option_c=request.form.get("option_c"),
            option_d=request.form.get("option_d"),
            correct_answer=request.form.get("correct_answer"),
        )
        db.session.add(q)
        db.session.commit()
        flash("Question added.", "success")
        return redirect(url_for("admin.quiz_questions", quiz_id=quiz_id))
    return render_template("admin/question_form.html", quiz=quiz, question=None)


@admin_bp.route("/questions/<int:question_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == "POST":
        question.question = request.form.get("question")
        question.question_type = request.form.get("question_type")
        question.option_a = request.form.get("option_a")
        question.option_b = request.form.get("option_b")
        question.option_c = request.form.get("option_c")
        question.option_d = request.form.get("option_d")
        question.correct_answer = request.form.get("correct_answer")
        db.session.commit()
        flash("Question updated.", "success")
        return redirect(url_for("admin.quiz_questions", quiz_id=question.quiz_id))
    return render_template("admin/question_form.html", quiz=question.quiz, question=question)


@admin_bp.route("/questions/<int:question_id>/delete", methods=["POST"])
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted.", "success")
    return redirect(url_for("admin.quiz_questions", quiz_id=quiz_id))


@admin_bp.route("/reports")
@admin_required
def reports():
    reports_list = Report.query.order_by(Report.created_at.desc()).all()
    return render_template("admin/reports.html", reports=reports_list)


@admin_bp.route("/reports/<int:report_id>/status", methods=["POST"])
@admin_required
def update_report_status(report_id):
    report = Report.query.get_or_404(report_id)
    report.status = request.form.get("status", "reviewed")
    db.session.commit()
    flash("Report status updated.", "success")
    return redirect(url_for("admin.reports"))
