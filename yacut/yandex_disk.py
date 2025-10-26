import asyncio
import os
import urllib.parse

import aiohttp

from yacut.constants import (
    YANDEX_DISK_API_HOST, YANDEX_DISK_API_VERSION,
    YANDEX_DISK_DOWNLOAD_URL, YANDEX_DISK_UPLOAD_URL
)


def _get_auth_headers():
    """Получает заголовки авторизации для API Яндекс.Диска."""
    disk_token = os.environ.get('DISK_TOKEN')
    return {'Authorization': f'OAuth {disk_token}'}


async def _create_folder_if_not_exists(session):
    """Создает папку Uploader на Яндекс.Диске, если она не существует."""
    folder_path = 'app:/Uploader'
    params = {'path': folder_path}

    async with session.get(
        url=f'{YANDEX_DISK_API_HOST}{YANDEX_DISK_API_VERSION}/disk/resources',
        headers=_get_auth_headers(),
        params=params
    ) as response:
        if response.status == 200:
            return True
    async with session.put(
        url=f'{YANDEX_DISK_API_HOST}{YANDEX_DISK_API_VERSION}/disk/resources',
        headers=_get_auth_headers(),
        params=params
    ) as response:
        return response.status in [200, 201]


async def _request_upload_url(session, filename):
    """Запрашивает URL для загрузки файла на Яндекс.Диск."""
    await _create_folder_if_not_exists(session)

    path = f'app:/{filename}'
    params = {
        'path': path,
        'overwrite': 'true'
    }

    async with session.get(
        url=YANDEX_DISK_UPLOAD_URL,
        headers=_get_auth_headers(),
        params=params
    ) as response:
        if response.status == 200:
            data = await response.json()
            return data.get('href')
        else:
            print(f"Ошибка запроса URL загрузки: {response.status}")
            text = await response.text()
            print(f"Ответ сервера: {text}")
        return None


async def _upload_file_to_disk(session, upload_url, file_data):
    """Загружает файл на Яндекс.Диск по предоставленному URL."""
    async with session.put(url=upload_url, data=file_data) as response:
        if response.status == 201:
            location = response.headers.get('Location', '')
            location = urllib.parse.unquote(location)
            location = location.replace('/disk', '')
            return location
        return None


async def _get_download_link(session, file_path):
    """Получает ссылку на скачивание файла с Яндекс.Диска."""
    params = {'path': file_path}

    async with session.get(
        url=YANDEX_DISK_DOWNLOAD_URL,
        headers=_get_auth_headers(),
        params=params
    ) as response:
        if response.status == 200:
            data = await response.json()
            return data.get('href')
        return None


async def _upload_single_file(session, filename, file_data):
    """Загружает один файл на Яндекс.Диск и возвращает ссылку на скачивание."""
    try:
        upload_url = await _request_upload_url(session, filename)
        if not upload_url:
            return filename, None

        file_path = await _upload_file_to_disk(session, upload_url, file_data)
        if not file_path:
            return filename, None

        download_link = await _get_download_link(session, file_path)
        return filename, download_link

    except Exception:
        return filename, None


async def upload_files_batch(files):
    """Асинхронно загружает несколько файлов на Яндекс.Диск."""
    async with aiohttp.ClientSession() as session:
        tasks = [
            _upload_single_file(
                session, file_storage.filename, file_storage.read())
            for file_storage in files
        ]
        results = await asyncio.gather(*tasks)
        return results
