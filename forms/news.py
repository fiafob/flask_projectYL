from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, MultipleFileField
from flask_wtf.file import FileAllowed
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    surname = StringField("Фамилия", validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    batya = StringField("Отчество")
    content = TextAreaField("Достижения", validators=[DataRequired()])
    image_form = MultipleFileField("Сканы достижений", validators=[DataRequired(), FileAllowed(
        ["jpg", "jpeg", "png"])])
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')
