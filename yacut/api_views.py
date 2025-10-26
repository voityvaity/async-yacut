from http import HTTPStatus

from flask import Blueprint, jsonify, request

from yacut.constants import API_ERROR_MESSAGES
from yacut.helpers import (
    create_short_link, create_url_mapping, get_url_map_by_short_id
)

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/id/', methods=['POST'])
def create_short_link_api():
    """Создание короткой ссылки через API."""
    try:
        json_data = request.get_json()
    except Exception:
        return jsonify(
            {'message': API_ERROR_MESSAGES['no_body']}
        ), HTTPStatus.BAD_REQUEST

    if json_data is None or json_data == {}:
        return jsonify(
            {'message': API_ERROR_MESSAGES['no_body']}
        ), HTTPStatus.BAD_REQUEST

    data = json_data

    if 'url' not in data or not data['url'].strip():
        return jsonify(
            {'message': API_ERROR_MESSAGES['url_required']}
        ), HTTPStatus.BAD_REQUEST

    original_url = data['url'].strip()
    custom_id = data.get('custom_id', '').strip() or None

    url_map, error_message = create_url_mapping(original_url, custom_id)

    if error_message:
        return jsonify({'message': error_message}), HTTPStatus.BAD_REQUEST

    short_link = create_short_link(request.url_root, url_map.short)

    return jsonify({
        'url': original_url,
        'short_link': short_link
    }), HTTPStatus.CREATED


@api_bp.route('/api/id/<short_id>/', methods=['GET'])
def get_original_url_api(short_id):
    """Получение оригинальной ссылки по короткому идентификатору."""
    url_map = get_url_map_by_short_id(short_id)

    if url_map:
        return jsonify(
            {'url': url_map.original}
        ), HTTPStatus.OK
    return jsonify(
        {'message': API_ERROR_MESSAGES['id_not_found']}
    ), HTTPStatus.NOT_FOUND
