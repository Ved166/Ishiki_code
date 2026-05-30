import os

from flask import Flask

from config import Config
from extensions import bcrypt, db, login_manager
from models import User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.admin import admin_bp
    from routes.analyzer import analyzer_bp
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.learning import learning_bp
    from routes.main import main_bp
    from routes.quiz import quiz_bp
    from routes.reports import reports_bp
    from routes.simulation import simulation_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(learning_bp, url_prefix="/learning")
    app.register_blueprint(analyzer_bp, url_prefix="/analyzer")
    app.register_blueprint(simulation_bp, url_prefix="/simulation")
    app.register_blueprint(quiz_bp, url_prefix="/quiz")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    with app.app_context():
        db.create_all()
        from seed import seed_database
        seed_database()

    return app
