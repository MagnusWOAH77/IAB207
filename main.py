from flask import Flask, abort, redirect, render_template, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from user import User
from database.base import db
from database.User import User as DBUser
from flask_bootstrap import Bootstrap
from datetime import datetime

from forms.signup import SignupForm
from forms.login import LoginForm
from forms.comment import CommentForm

from forms.event import EventForm
from database.Event import Event
from database.Comments import Comments
from database.UserEvents import UserEvents

import os

import bcrypt

GENERIC_ACKNOWLEDGEMENT_TEXT = (
    "We acknowledge the Traditional Custodians of the land on which this event takes place. "
    "We pay our respects to Elders past and present, and recognise the continuing connection "
    "of Aboriginal and Torres Strait Islander peoples to land, waters, culture and community."
)


def build_acknowledgement_values(form):
    acknowledgement_type = form.acknowledgement_type.data

    if acknowledgement_type == "None":
        return None, None, None

    acknowledgement_city = form.acknowledgement_city.data.strip() if form.acknowledgement_city.data else None
    traditional_custodians = form.traditional_custodians.data.strip() if form.traditional_custodians.data else None

    if acknowledgement_type == "Generic":
        acknowledgement_text = GENERIC_ACKNOWLEDGEMENT_TEXT
    else:
        acknowledgement_text = form.acknowledgement_text.data.strip() if form.acknowledgement_text.data else ""

    return acknowledgement_city, traditional_custodians, acknowledgement_text


app = Flask(__name__)
app.config["SECRET_KEY"] = "123"
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.db"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db.init_app(app)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.get_user(user_id)

@app.route("/")
def index():
    selected_genre = request.args.get("genre")
    search = request.args.get("search")

    query = db.select(Event)

    if selected_genre:
        query = query.where(Event.genres.contains(selected_genre))

    if search:
        query = query.where(Event.name.contains(search))

    events = db.session.execute(query.order_by(Event.event_datetime)).scalars().all()

    for event in events:
        event.update_status()

    db.session.commit()

    events_for_js = []

    for event in events:
        events_for_js.append({
            "preview_image": url_for("static", filename="uploads/" + (event.image_filename or "event.jpg")),
            "name": event.name,
            "eid": event.id,
            "date": event.event_datetime.isoformat(),
            "genreText": event.genres,
            "price": event.price if event.price is not None else 0,
            "status": event.status,
            "location": event.location
        })

    return render_template(
        "index.html",
        title="Home",
        events=events,
        events_for_js=events_for_js,
        selected_genre=selected_genre,
        search=search
    )

@app.route("/event-create", methods=["GET", "POST"])
@login_required
def create_event_page():
    form = EventForm()

    if form.validate_on_submit():
        event_datetime = datetime.strptime(form.event_datetime.data, "%Y-%m-%d %H:%M")

        # image_file = form.image if form.image != None else "event.jpg"

        acknowledgement_city, traditional_custodians, acknowledgement_text = build_acknowledgement_values(form)

        event = Event(
            name=form.name.data,
            event_datetime=event_datetime,
            location=form.location.data,
            genres=", ".join(form.genres.data),
            price=float(form.price.data),
            tickets_available=form.tickets_available.data,
            overview=form.overview.data,
            acknowledgement_type=form.acknowledgement_type.data,
            acknowledgement_city=acknowledgement_city,
            traditional_custodians=traditional_custodians,
            acknowledgement_text=acknowledgement_text,
            owner_id=int(current_user.get_id()),
            image_filename="event.jpg"
        )

        event.update_status()

        db.session.add(event)
        db.session.commit()

        if form.image.data is not None:
            thumbnail = form.image.data
            _, extension = os.path.splitext(secure_filename(thumbnail.filename))
            thumbnail_name = str(event.id) + extension
            thumbnail_filepath = os.path.join(app.config['UPLOAD_FOLDER'], thumbnail_name)
            thumbnail.save(thumbnail_filepath)

            event.image_filename = thumbnail_name
            db.session.commit()

        flash("Event created successfully.", "success")
        return redirect(url_for("event_details_page", event_id=event.id))
    else:
        print(form.errors)

    return render_template("event-create.html", title="Create Event", form=form)

@app.route("/event-details/<int:event_id>", methods=["GET", "POST"])
def event_details_page(event_id):

    comment_form = CommentForm()

    if comment_form.validate_on_submit():

        comment = Comments(
            event_id=event_id,
            user_id=current_user.user_id,
            text=comment_form.comment.data
        )

        db.session.add(comment)
        db.session.commit()

    event = db.get_or_404(Event, event_id)

    existing_booking = None

    if current_user.is_authenticated:
        existing_booking = db.session.execute(
            db.select(UserEvents)
            .where(UserEvents.user_id == int(current_user.get_id()))
            .where(UserEvents.event_id == event.id)
        ).scalars().first()

    event.update_status()
    db.session.commit()

    comments = db.session.execute(
        db.select(Comments, DBUser)
        .join(DBUser)
        .where(Comments.user_id == DBUser.id)
        .where(Comments.event_id == int(event_id))
        .order_by(Comments.created_at)
    ).all()

    return render_template(
        "event-details.html",
        title=event.name,
        event=event,
        comments=comments,
        comment_form=comment_form,
        existing_booking=existing_booking
    )

@app.route("/delete_comment<int:comment_id>", methods=["GET"])
def delete_comment(comment_id):

    if not current_user.is_authenticated:
        return redirect(request.referrer or url_for('index'))

    comment = db.session.get(Comments, comment_id)

    if comment.user_id == current_user.user_id:
        db.session.delete(comment)
        db.session.commit()

    return redirect(request.referrer or url_for('index'))

@app.route("/my-events")
@login_required
def my_events_page():
    events = db.session.execute(
        db.select(Event)
        .where(Event.owner_id == int(current_user.get_id()))
        .order_by(Event.event_datetime)
    ).scalars().all()

    for event in events:
        event.update_status()

    db.session.commit()

    return render_template("my-events.html", title="My Events", events=events)

@app.route("/event/<int:event_id>/cancel", methods=["POST"])
@login_required
def cancel_event(event_id):
    event = db.get_or_404(Event, event_id)

    if event.owner_id != int(current_user.get_id()):
        abort(403)

    event.status = "Cancelled"
    db.session.commit()

    flash("Event cancelled.", "success")
    return redirect(url_for("my_events_page"))

@app.route("/history")
@login_required
def history_page():
    booked_events = db.session.execute(
        db.select(UserEvents, Event)
        .join(Event, UserEvents.event_id == Event.id)
        .where(UserEvents.user_id == int(current_user.get_id()))
        .order_by(UserEvents.booked_at.desc())
    ).all()

    return render_template(
        "history.html",
        title="History",
        booked_events=booked_events
    )

@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    form = SignupForm()

    if form.validate_on_submit():

        if form.password.data != form.confirm_password.data:
            return render_template(
                "signup.html",
                title="Sign Up",
                form=form,
                alerts=["Passwords do not match"]
            )

        if len(str(form.phone_number.data)) != 10:
            return render_template(
                "signup.html",
                title="Sign Up",
                form=form,
                alerts=["Phone number must be exactly 10 digits"]
            )

        password_hash = bcrypt.hashpw(form.password.data.encode("utf-8"), bcrypt.gensalt())

        try:
            user = DBUser(
                username=form.username.data,
                password=password_hash.decode("utf-8"),
                email=form.email.data,
                first_name=form.first_name.data,
                surname=form.surname.data,
                phone_number=form.phone_number.data,
                address=form.address.data
            )

            db.session.add(user)
            db.session.commit()

        except:
            return render_template(
                "signup.html",
                title="Sign Up",
                form=form,
                alerts=["Username or email already exists"]
            )

        login_user(User(user.id, user.username, user.password))
        return redirect(url_for("index"))

    return render_template("signup.html", title="Sign Up", form=form, alerts=[])

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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("login_page"))

@app.route("/event/<int:event_id>/book", methods=["POST"])
@login_required
def book_event(event_id):
    event = db.get_or_404(Event, event_id)
    if event.status == "Cancelled":
        flash("This event has been cancelled and cannot be booked.", "danger")
        return redirect(url_for("event_details_page", event_id=event.id))

    existing_booking = db.session.execute(
        db.select(UserEvents)
        .where(UserEvents.user_id == int(current_user.get_id()))
        .where(UserEvents.event_id == event.id)
    ).scalars().first()

    if existing_booking:
        flash("You have already booked this event.", "warning")
        return redirect(url_for("event_details_page", event_id=event.id))

    if event.tickets_available <= 0:
        flash("This event is sold out.", "danger")
        return redirect(url_for("event_details_page", event_id=event.id))

    booking = UserEvents(
        user_id=int(current_user.get_id()),
        event_id=event.id
    )

    event.tickets_available -= 1
    event.update_status()

    db.session.add(booking)
    db.session.commit()

    flash("Event booked successfully.", "success")
    return redirect(url_for("history_page"))

@app.route("/event/<int:event_id>/cancel-booking", methods=["POST"])
@login_required
def cancel_booking(event_id):
    event = db.get_or_404(Event, event_id)

    booking = db.session.execute(
        db.select(UserEvents)
        .where(UserEvents.user_id == int(current_user.get_id()))
        .where(UserEvents.event_id == event.id)
    ).scalars().first()

    if not booking:
        flash("You do not have a booking for this event.", "warning")
        return redirect(url_for("event_details_page", event_id=event.id))

    db.session.delete(booking)
    event.tickets_available += 1
    event.update_status()

    db.session.commit()

    flash("Booking cancelled.", "success")
    return redirect(url_for("event_details_page", event_id=event.id))   

if __name__ == "__main__":
    app.run(debug=True)