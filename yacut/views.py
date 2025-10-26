from flask import (
    Blueprint, abort, flash, redirect, render_template, request
)

from yacut.forms import FileUploadForm, URLForm
from yacut.helpers import (
    create_short_link, create_url_mapping, flash_form_errors,
    get_url_map_by_short_id, is_file_url, is_reserved_route
)
from yacut.utils import is_valid_short_id_format

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
        flash(f'Ваша новая ссылка готова: {short_link}', 'success')
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
            import asyncio
            from yacut.yandex_disk import upload_files_batch
            import os

            # Проверяем наличие токена
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

            files_count = len(file_links)
            flash(f'Обработано файлов: {files_count}', 'success')
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
        abort(404)

    if not is_valid_short_id_format(short_id):
        abort(404)

    url_map = get_url_map_by_short_id(short_id)

    if url_map:
        if is_file_url(url_map.original):
            response = redirect(url_map.original)
            response.headers['Content-Disposition'] = 'attachment'
            return response
        else:
            return redirect(url_map.original)
    else:
        abort(404)
