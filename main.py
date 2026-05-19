from flask import Flask, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from user import User
from database.base import db
from database.User import User as DBUser
from flask_bootstrap import Bootstrap

from forms.signup import SignupForm
from forms.login import LoginForm
import bcrypt

app = Flask(__name__)
app.config["SECRET_KEY"] = "123"
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.db"
db.init_app(app)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.get_user(user_id)

@app.route("/")
@login_required
def index():
    return render_template("index.html", title="Home")

@app.route("/event-create")
@login_required
def create_event_page():
    return render_template("event-create.html", title="Create Event")

@app.route("/event-details")
@login_required
def event_details_page():
    return render_template("event-details.html", title="Event Details")

@app.route("/my-events")
@login_required
def my_events_page():
    return render_template("my-events.html", title="My Events")

@app.route("/history")
@login_required
def history_page():
    return render_template("history.html", title="History")

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    form = SignupForm()

    # Form handling
    if form.validate_on_submit():
    
        # passwords confirmation match
        if form.password.data != form.confirm_password.data:
            print("Passwords do not match!")
            return render_template("signup.html", title="Sign Up", form=form)
        
        # hash password
        password_hash = bcrypt.hashpw(form.password.data.encode("utf-8"), bcrypt.gensalt())

        print()

        # create user
        user = DBUser(username=form.username.data, password=password_hash.decode("utf-8"))
        db.session.add(user)
        db.session.commit()

        #login
        login_user(User(user.id, user.username, user.password))
        return redirect(url_for("index"))
    
    return render_template("signup.html", title="Sign Up", form=form)

@app.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()

    # form handler
    if form.validate_on_submit():

        # get user by username
        user = db.session.execute(db.select(DBUser).where(DBUser.username == form.username.data)).scalars().first()

        # check if password is correct
        if not user or not bcrypt.checkpw(form.password.data.encode("utf-8"), user.password.encode("utf-8")):
            print("Invalid username or password!")
            return render_template("login.html", title="Login", form=form)

        # Login
        login_user(User(user.id, user.username, user.password))
        return redirect(url_for("index"))
    return render_template("login.html", title="Login", form=form)

if __name__ == "__main__":
    app.run(debug=True)