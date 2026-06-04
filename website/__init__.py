from flask import Flask
from website.database.base import db
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from website.user import User
import os

from website.database.base import db
from website.database.User import User as DBUser
from website.database.Event import Event
from website.database.Comments import Comments
from website.database.UserEvents import UserEvents

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "123"
    bootstrap = Bootstrap(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "main.login_page"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.db"
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
    db.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_user(user_id)

    with app.app_context():
        db.create_all()

    from website.routes import main_bp
    app.register_blueprint(main_bp)

    return app