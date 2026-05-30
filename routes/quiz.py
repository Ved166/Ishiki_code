import random

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Question, Quiz, Result
from services.gamification import award_xp, log_activity, update_streak

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/")
@login_required
def quiz_list():
    quizzes = Quiz.query.all()
    past = {
        r.quiz_id: r
        for r in Result.query.filter_by(user_id=current_user.id).all()
    }
    return render_template("quiz/list.html", quizzes=quizzes, past=past)


@quiz_bp.route("/<int:quiz_id>", methods=["GET", "POST"])
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = list(Question.query.filter_by(quiz_id=quiz_id).all())
    if not questions:
        flash("This quiz has no questions yet.", "warning")
        return redirect(url_for("quiz.quiz_list"))

    if request.method == "POST" and request.form.get("action") == "submit":
        score = 0
        review = []
        for q in questions:
            user_ans = request.form.get(f"q_{q.id}", "")
            correct = q.correct_answer
            if q.question_type == "true_false":
                is_correct = user_ans == correct
            elif q.question_type == "multiple_choice":
                letter_map = {"a": q.option_a, "b": q.option_b, "c": q.option_c, "d": q.option_d}
                is_correct = letter_map.get(user_ans) == correct
            else:
                letter_map = {"a": q.option_a, "b": q.option_b, "c": q.option_c, "d": q.option_d}
                is_correct = letter_map.get(user_ans) == correct
            if is_correct:
                score += 1
            review.append({"question": q, "user_answer": user_ans, "correct": is_correct})

        total = len(questions)
        db.session.add(Result(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=score,
            total=total,
        ))
        pct = (score / total) * 100
        xp = int(20 + pct * 0.5)
        update_streak(current_user)
        award_xp(current_user, xp, f"Quiz: {quiz.title}")
        log_activity(current_user.id, "Quiz completed", f"{score}/{total}")
        db.session.commit()
        session.pop(f"quiz_{quiz_id}_order", None)
        return render_template(
            "quiz/results.html",
            quiz=quiz,
            score=score,
            total=total,
            review=review,
        )

    order_key = f"quiz_{quiz_id}_order"
    if order_key not in session:
        order = list(range(len(questions)))
        random.shuffle(order)
        session[order_key] = order
    else:
        order = session[order_key]
    ordered_questions = [questions[i] for i in order]

    return render_template(
        "quiz/take.html",
        quiz=quiz,
        questions=ordered_questions,
        timer_seconds=300,
    )
