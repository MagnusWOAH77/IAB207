from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", title="Home")

@app.route("/event-create")
def create_event_page():
    return render_template("event-create.html", title="Create Event")

@app.route("/event-details")
def event_details_page():
    return render_template("event-details.html", title="Event Details")

@app.route("/my-events")
def my_events_page():
    return render_template("my-events.html", title="My Events")

@app.route("/history")
def history_page():
    return render_template("history.html", title="History")