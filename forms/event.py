from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectMultipleField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired


class EventForm(FlaskForm):
    name = StringField("Event Name", validators=[DataRequired()])
    event_datetime = StringField("Date and Time", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])

    image = FileField("Upload Image", validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only (.jpg, .png)!')
    ])

    genres = SelectMultipleField(
        "Genres",
        choices=[
            ("Rock", "Rock"),
            ("Metal", "Metal"),
            ("Alt", "Alt"),
            ("Pop", "Pop"),
            ("Jazz", "Jazz"),
            ("Electronic", "Electronic"),
        ],
        validators=[DataRequired()]
    )

    price = DecimalField("Price", validators=[DataRequired(), NumberRange(min=0)])
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

    acknowledgement_text = TextAreaField("Acknowledgement Text")

    submit = SubmitField("Create Event")