import asyncio
import os
import urllib.parse

import requests
from flask import (
    Blueprint, abort, flash, redirect, render_template, request, Response
)
from http import HTTPStatus

from yacut.forms import FileUploadForm, URLForm
from yacut.helpers import (
    create_short_link, create_url_mapping, flash_form_errors,
    get_url_map_by_short_id, is_file_url, is_reserved_route
)
from yacut.utils import is_valid_short_id_format
from yacut.yandex_disk import upload_files_batch


bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    """Главная страница для создания коротких ссылок."""
    form = URLForm()

    if form.validate_on_submit():
        original_url = form.original_link.data.strip()
        custom_id = (form.custom_id.data.strip()
                     if form.custom_id.data else None)

        url_map, error_message = create_url_mapping(original_url, custom_id)

        if error_message:
            flash(error_message, 'error')
            return render_template('index.html', form=form)

        short_link = create_short_link(request.url_root, url_map.short)
        return render_template('index.html', form=form, short_link=short_link)

    flash_form_errors(form)

    return render_template('index.html', form=form)


@bp.route('/files', methods=['GET', 'POST'])
def files():
    """Страница загрузки файлов на Яндекс.Диск."""
    form = FileUploadForm()

    if form.validate_on_submit():
        uploaded_files = form.files.data

        if not uploaded_files:
            flash('Выберите хотя бы один файл для загрузки.', 'error')
            return render_template('files.html', form=form)

        try:
            disk_token = os.environ.get('DISK_TOKEN')
            if not disk_token:
                flash('Не настроен токен Яндекс.Диска. '
                      'Обратитесь к администратору.', 'error')
                return render_template('files.html', form=form)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            upload_results = loop.run_until_complete(
                upload_files_batch(uploaded_files))
            loop.close()

            file_links = []
            for filename, download_link in upload_results:
                if download_link:
                    url_map, error = create_url_mapping(download_link)
                    if url_map:
                        short_link = create_short_link(
                            request.url_root, url_map.short)
                        file_links.append({
                            'filename': filename,
                            'short_link': short_link
                        })
                    else:
                        file_links.append({
                            'filename': filename,
                            'short_link': None,
                            'error': 'Не удалось создать короткую ссылку'
                        })
                else:
                    file_links.append({
                        'filename': filename,
                        'short_link': None,
                        'error': 'Не удалось загрузить файл на Яндекс.Диск'
                    })

            return render_template(
                'files.html', form=form, file_links=file_links
            )

        except Exception:
            flash('Произошла ошибка при загрузке файлов. '
                  'Попробуйте еще раз.', 'error')
            return render_template('files.html', form=form)

    flash_form_errors(form)

    return render_template('files.html', form=form)


@bp.route('/<short_id>')
def redirect_to_original(short_id):
    """Переадресация на оригинальную ссылку."""
    if is_reserved_route(short_id):
        abort(HTTPStatus.NOT_FOUND)

    if not is_valid_short_id_format(short_id):
        abort(HTTPStatus.NOT_FOUND)

    url_map = get_url_map_by_short_id(short_id)

    if not url_map:
        abort(HTTPStatus.NOT_FOUND)

    if is_file_url(url_map.original):
        try:
            response = requests.get(url_map.original, stream=True)
        except Exception:
            abort(HTTPStatus.NOT_FOUND)

        if response.status_code != HTTPStatus.OK:
            abort(HTTPStatus.NOT_FOUND)

        parsed_url = urllib.parse.urlparse(url_map.original)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        filename = query_params.get('filename', ['file'])[0]
        encoded_filename = urllib.parse.quote(
            filename.encode('utf-8'))

        return Response(
            response.content,
            mimetype=response.headers.get(
                'content-type', 'application/octet-stream'),
            headers={
                'Content-Disposition': (
                    f'attachment; filename*=UTF-8\'\''
                    f'{encoded_filename}'
                )
            }
        )

    return redirect(url_map.original)
