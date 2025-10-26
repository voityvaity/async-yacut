import string

# Константы для валидации
MAX_SHORT_ID_LENGTH = 16
MIN_SHORT_ID_LENGTH = 6
RESERVED_WORDS = ['files']
VALID_CHARS = string.ascii_letters + string.digits

# Константы для маршрутов и доменов
RESERVED_ROUTES = ['files', 'api', 'static']
FILE_DOMAINS = ['yandex.ru', 'cloud-api.yandex.net']

# Сообщения об ошибках
ERROR_MESSAGES = {
    'invalid_format': 'Указано недопустимое имя для короткой ссылки',
    'already_exists': 'Предложенный вариант короткой ссылки уже существует.',
    'too_long': 'Длина не должна превышать 16 символов'
}

# Сообщения для API
API_ERROR_MESSAGES = {
    'no_body': 'Отсутствует тело запроса',
    'url_required': '"url" является обязательным полем!',
    'id_not_found': 'Указанный id не найден',
    'creation_error': 'Произошла ошибка при создании короткой ссылки',
    'request_error': 'Произошла ошибка при обработке запроса'
}

# Константы для Яндекс.Диска
YANDEX_DISK_API_HOST = 'https://cloud-api.yandex.net/'
YANDEX_DISK_API_VERSION = 'v1'
YANDEX_DISK_UPLOAD_URL = (
    f'{YANDEX_DISK_API_HOST}{YANDEX_DISK_API_VERSION}/disk/resources/upload'
)
YANDEX_DISK_DOWNLOAD_URL = (
    f'{YANDEX_DISK_API_HOST}{YANDEX_DISK_API_VERSION}/disk/resources/download'
)
YANDEX_DISK_UPLOAD_PATH_PREFIX = 'app:/'
