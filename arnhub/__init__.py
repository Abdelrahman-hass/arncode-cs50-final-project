import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from datetime import datetime
from werkzeug.security import generate_password_hash
from .models import db, User

mail = Mail()

def create_app():
    app = Flask(__name__, template_folder="templates")

    # -----------------------
    # Configuration
    # -----------------------
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') or 'sqlite:///db.sqlite'
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'lesson_videos')

    # 📧 Email settings
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'arncode.app@gmail.com'
    app.config['MAIL_PASSWORD'] = 'wnkaerekpmqixgkj'
    app.config['MAIL_DEFAULT_SENDER'] = 'arncode.app@gmail.com'

    # -----------------------
    # Initialize extensions
    # -----------------------
    db.init_app(app)
    migrate = Migrate(app, db)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # -----------------------
    # Load user callback
    # -----------------------
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -----------------------
    # Create Admin User
    # -----------------------
    @app.before_first_request
    def create_admin():
        with app.app_context():
            if not User.query.filter_by(username="ARNcode").first():
                admin = User(
                    username="ARNcode",
                    email="arncode.app@gmail.com",
                    password=generate_password_hash("Abd123an@", method="sha256"),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin created:", admin.username)
            else:
                print("⚠️ Admin already exists.")

    # -----------------------
    # Blueprints
    # -----------------------
    from .auth import auth_bp
    from .routes import main as main_bp
    from .admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # -----------------------
    # Create tables
    # -----------------------
    with app.app_context():
        db.create_all()

    # -----------------------
    # Template context
    # -----------------------
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    return app