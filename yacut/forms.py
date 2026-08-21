from flask_wtf import FlaskForm
from wtforms import StringField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from .constants import SHORT_ID_PATTERN, SHORT_MAX_LENGTH


class LinkForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[DataRequired(), Length(max=2048)]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=SHORT_MAX_LENGTH),
            Regexp(SHORT_ID_PATTERN, message='Только латинские буквы и цифры')
        ]
    )
    submit = SubmitField('Создать')


class FileUploadForm(FlaskForm):
    files = MultipleFileField('Выберите файлы', validators=[DataRequired()])
    submit = SubmitField('Загрузить')