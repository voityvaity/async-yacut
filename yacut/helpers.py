from flask import flash, jsonify, render_template, request

from yacut.constants import API_ERROR_MESSAGES, FILE_DOMAINS, RESERVED_ROUTES
from yacut.models import URLMap


def flash_form_errors(form):
    """Отображает ошибки валидации формы."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'error')


def is_reserved_route(short_id):
    """Проверяет, является ли short_id зарезервированным маршрутом."""
    return short_id in RESERVED_ROUTES


def is_file_url(url):
    """Проверяет, является ли URL ссылкой на файл."""
    return any(domain in url for domain in FILE_DOMAINS)


def get_url_map_by_short_id(short_id):
    """Получает URLMap по короткому идентификатору."""
    return URLMap.query.filter_by(short=short_id).first()


def create_short_link(base_url, short_id):
    """Создает полную короткую ссылку."""
    return f'{base_url}{short_id}'


def create_url_mapping(original_url, custom_id=None):
    """Создает запись URLMap с валидацией и сохранением в БД."""
    from yacut.utils import validate_custom_id, get_unique_short_id
    from yacut import db

    if custom_id:
        is_valid, error_message = validate_custom_id(custom_id)
        if not is_valid:
            return None, error_message
        short_id = custom_id
    else:
        short_id = get_unique_short_id()

    try:
        url_map = URLMap(original=original_url, short=short_id)
        db.session.add(url_map)
        db.session.commit()
        return url_map, None
    except Exception:
        db.session.rollback()
        return None, API_ERROR_MESSAGES['creation_error']


def _is_api_request():
    """Проверяет, является ли запрос API запросом."""
    return request.path.startswith('/api/')


def _create_error_response(status_code, message, template):
    """Создает ответ об ошибке в зависимости от типа запроса."""
    if _is_api_request():
        return jsonify({'message': message}), status_code
    return render_template(template), status_code


def register_error_handlers(app):
    """Регистрирует обработчики ошибок для приложения."""

    @app.errorhandler(400)
    def bad_request_error(error):
        """Обработчик ошибки 400."""
        if _is_api_request():
            if ('json' in str(error).lower() or
                    'parse' in str(error).lower()):
                return jsonify(
                    {'message': API_ERROR_MESSAGES['no_body']}
                ), 400
        return _create_error_response(400, 'Неверный запрос', '400.html')

    @app.errorhandler(404)
    def not_found_error(error):
        """Обработчик ошибки 404."""
        return _create_error_response(
            404, API_ERROR_MESSAGES['id_not_found'], '404.html'
        )

    @app.errorhandler(500)
    def internal_error(error):
        """Обработчик ошибки 500."""
        return _create_error_response(
            500, 'Внутренняя ошибка сервера', '500.html'
        )

    @app.errorhandler(413)
    def request_entity_too_large_error(error):
        """Обработчик ошибки 413."""
        return _create_error_response(
            413, 'Файл слишком большой', '413.html'
        )
