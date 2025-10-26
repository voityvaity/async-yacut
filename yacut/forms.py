from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, MultipleFileField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, URL, ValidationError

from yacut.constants import ERROR_MESSAGES, MAX_SHORT_ID_LENGTH
from yacut.utils import validate_custom_id as validate_custom_id_utils

FORM_CONTROL_CLASS = 'form-control form-control-lg py-2 mb-3'
BUTTON_CLASS = 'btn btn-primary'


class URLForm(FlaskForm):
    """Форма для создания коротких ссылок."""

    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Некорректный URL')
        ],
        render_kw={'class': FORM_CONTROL_CLASS,
                   'placeholder': 'Длинная ссылка'}
    )

    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Length(max=MAX_SHORT_ID_LENGTH, message=ERROR_MESSAGES['too_long'])
        ],
        render_kw={'class': FORM_CONTROL_CLASS,
                   'placeholder': 'Ваш вариант короткой ссылки'}
    )

    submit = SubmitField(
        'Создать',
        render_kw={'class': BUTTON_CLASS}
    )

    def validate_custom_id(self, field):
        """Валидация пользовательского варианта."""
        if field.data:
            is_valid, error_message = validate_custom_id_utils(field.data)
            if not is_valid:
                raise ValidationError(error_message)


class FileUploadForm(FlaskForm):
    """Форма для загрузки файлов."""

    files = MultipleFileField(
        'Выберите файлы для загрузки',
        validators=[
            DataRequired(message='Выберите хотя бы один файл'),
            FileAllowed([
                'jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt', 'doc',
                'docx', 'xls', 'xlsx', 'zip', 'rar'
            ], message='Недопустимый тип файла')
        ],
        render_kw={'class': 'form-control', 'multiple': True}
    )

    submit = SubmitField(
        'Загрузить файлы',
        render_kw={'class': BUTTON_CLASS}
    )
