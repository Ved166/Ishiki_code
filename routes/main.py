from flask import Blueprint, render_template
from flask_login import current_user

from models import User

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    top_users = User.query.filter_by(role="user").order_by(User.xp.desc()).limit(5).all()
    return render_template("home.html", top_users=top_users)
