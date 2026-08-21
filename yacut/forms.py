from flask_wtf import FlaskForm
from wtforms import StringField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from .constants import (
    SHORT_PATTERN,
    SHORT_MAX_LENGTH,
    ORIGINAL_MAX_LENGTH,
    INVALID_SHORT_FORM,
)


class LinkForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[DataRequired(), Length(max=ORIGINAL_MAX_LENGTH)]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=SHORT_MAX_LENGTH),
            Regexp(SHORT_PATTERN, message=INVALID_SHORT_FORM)
        ]
    )
    submit = SubmitField('Создать')


class FileUploadForm(FlaskForm):
    files = MultipleFileField('Выберите файлы', validators=[DataRequired()])
    submit = SubmitField('Загрузить')
