from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Module, ModuleProgress
from services.gamification import award_xp, log_activity, update_streak

learning_bp = Blueprint("learning", __name__)


@learning_bp.route("/")
@login_required
def modules_list():
    modules = Module.query.order_by(Module.order_index).all()
    progress_map = {
        p.module_id: p
        for p in ModuleProgress.query.filter_by(user_id=current_user.id).all()
    }
    return render_template(
        "learning/modules.html",
        modules=modules,
        progress_map=progress_map,
    )


@learning_bp.route("/<int:module_id>")
@login_required
def module_detail(module_id):
    module = Module.query.get_or_404(module_id)
    progress = ModuleProgress.query.filter_by(
        user_id=current_user.id, module_id=module_id
    ).first()
    return render_template("learning/module_detail.html", module=module, progress=progress)


@learning_bp.route("/<int:module_id>/complete", methods=["POST"])
@login_required
def complete_module(module_id):
    module = Module.query.get_or_404(module_id)
    progress = ModuleProgress.query.filter_by(
        user_id=current_user.id, module_id=module_id
    ).first()
    if not progress:
        progress = ModuleProgress(user_id=current_user.id, module_id=module_id)
        db.session.add(progress)
    if not progress.completed:
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        update_streak(current_user)
        award_xp(current_user, 50, f"Completed module: {module.title}")
        log_activity(current_user.id, "Module completed", module.title)
        db.session.commit()
        flash(f"Module '{module.title}' completed! +50 XP", "success")
    else:
        flash("Module already completed.", "info")
    return redirect(url_for("learning.module_detail", module_id=module_id))
