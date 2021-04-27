from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class CommsForm(FlaskForm):
    comment = TextAreaField("Leave a comment", validators=[DataRequired()])
    anonymous = BooleanField("povezlo povezlo")
    submit = SubmitField("Submit")