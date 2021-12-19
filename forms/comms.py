from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class CommsForm(FlaskForm):
    comment = TextAreaField("Оставьте комментарий", validators=[DataRequired()])
    anonymous = BooleanField("Оставить комментарий анонимно")
    submit = SubmitField("Тык")