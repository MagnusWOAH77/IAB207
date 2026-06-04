from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectMultipleField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired


class EventForm(FlaskForm):
    name = StringField("Event Name", validators=[DataRequired()])
    event_datetime = StringField("Date and Time")
    location = StringField("Location", validators=[DataRequired()])

    image = FileField("Upload Image", validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only (.jpg, .png)!')
    ])

    genres = SelectMultipleField(
        "Genres",
        choices=[
            ("Metal", "Metal"),
            ("Rock", "Rock"),
            ("Alt", "Alt"),
            ("Rap", "Rap"),
            ("Pop", "Pop"),
            ("Jazz", "Jazz"),
            ("Country", "Country"),
            ("Electronic", "Electronic"),

            ("Football", "Football"),
            ("Basketball", "Basketball"),
            ("Running", "Running"),
            ("Cycling", "Cycling"),
            ("Fitness", "Fitness"),
            ("Motorsport", "Motorsport"),

            ("Comedy", "Comedy"),
            ("Theatre", "Theatre"),
            ("Film", "Film"),
            ("Dance", "Dance"),
            ("Exhibition", "Exhibition"),
            ("Workshop", "Workshop"),

            ("Food Festival", "Food Festival"),
            ("Wine", "Wine"),
            ("Markets", "Markets"),
            ("Cooking Class", "Cooking Class"),
            ("Street Food", "Street Food"),

            ("Family", "Family"),
            ("Charity", "Charity"),
            ("Networking", "Networking"),
            ("Education", "Education"),
            ("Meetup", "Meetup")
        ],
        validators=[DataRequired()]
    )

    price = DecimalField("Price", validators=[NumberRange(min=0)])
    tickets_available = IntegerField("Tickets Available", validators=[DataRequired(), NumberRange(min=0)])

    overview = TextAreaField("Overview", validators=[DataRequired()])

    acknowledgement_type = SelectField(
        "Acknowledgement of Country",
        choices=[
            ("None", "No Acknowledgement of Country"),
            ("Generic", "Acknowledgement of Country: generic"),
            ("Enhanced", "Acknowledgement of Country: enhanced"),
        ],
        validators=[DataRequired()]
    )

    acknowledgement_city = StringField("Event City / Place")
    traditional_custodians = StringField("Traditional Custodians / Traditional Owners")
    acknowledgement_text = TextAreaField("Enhanced Acknowledgement Text")

    submit = SubmitField("Create Event")