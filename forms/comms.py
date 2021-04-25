from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, SubmitField


class CommsForm(FlaskForm):
    comment = TextAreaField("Leave a comment")
    anonymous = BooleanField("povezlo povezlo")
    submit = SubmitField("Submit")