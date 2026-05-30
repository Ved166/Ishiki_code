from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required

from extensions import db
from models import SimulationAttempt
from seed import get_email_scenarios, get_web_scenarios
from services.gamification import award_xp, log_activity

simulation_bp = Blueprint("simulation", __name__)


@simulation_bp.route("/")
@login_required
def index():
    return render_template("simulation/index.html")


@simulation_bp.route("/email")
@login_required
def email_simulation():
    scenarios = get_email_scenarios()
    idx = int(request.args.get("n", 0)) % len(scenarios)
    return render_template(
        "simulation/email.html",
        scenario=scenarios[idx],
        index=idx,
        total=len(scenarios),
    )


@simulation_bp.route("/website")
@login_required
def website_simulation():
    scenarios = get_web_scenarios()
    idx = int(request.args.get("n", 0)) % len(scenarios)
    return render_template(
        "simulation/website.html",
        scenario=scenarios[idx],
        index=idx,
        total=len(scenarios),
    )


@simulation_bp.route("/check", methods=["POST"])
@login_required
def check_answer():
    data = request.get_json() or {}
    sim_type = data.get("type")
    index = int(data.get("index", 0))
    answer = data.get("answer", "").lower()

    if sim_type == "email":
        scenarios = get_email_scenarios()
        scenario = scenarios[index % len(scenarios)]
        correct_label = "phishing" if scenario["is_phishing"] else "safe"
        is_correct = answer == correct_label
        feedback = scenario["feedback"]
    elif sim_type == "website":
        scenarios = get_web_scenarios()
        scenario = scenarios[index % len(scenarios)]
        correct_label = "fake" if scenario["is_fake"] else "safe"
        is_correct = answer == correct_label
        feedback = scenario["feedback"]
    else:
        return jsonify({"error": "Invalid type"}), 400

    db.session.add(SimulationAttempt(
        user_id=current_user.id,
        scenario_type=sim_type,
        scenario_id=index,
        user_answer=answer,
        correct=is_correct,
    ))
    if is_correct:
        award_xp(current_user, 15, f"Correct {sim_type} simulation")
        log_activity(current_user.id, "Simulation correct", sim_type)
    db.session.commit()

    return jsonify({
        "correct": is_correct,
        "feedback": feedback,
        "correct_answer": correct_label,
    })
