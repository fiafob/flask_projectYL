from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    surname = StringField("Surname", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    batya = StringField("Patronymic")
    content = TextAreaField("Achievements", validators=[DataRequired()])
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')