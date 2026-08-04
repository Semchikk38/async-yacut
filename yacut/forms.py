# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

class LinkForm(FlaskForm):
    original_link = StringField('Длинная ссылка', validators=[DataRequired()])
    custom_id = StringField('Ваш вариант короткой ссылки', validators=[
        Optional(),
        Length(max=16, message='Максимальная длина 16 символов'),
        Regexp(r'^[A-Za-z0-9]*$', message='Только латинские буквы и цифры')
    ])
    submit = SubmitField('Создать')

class FileUploadForm(FlaskForm):
    files = MultipleFileField('Выберите файлы', validators=[DataRequired()])
    submit = SubmitField('Загрузить')
