import random
import time

from yacut.constants import (
    ERROR_MESSAGES, MAX_SHORT_ID_LENGTH, MIN_SHORT_ID_LENGTH,
    RESERVED_WORDS, VALID_CHARS
)
from yacut.models import URLMap


def _check_short_id_exists(short_id):
    """Проверяет существование короткого идентификатора в БД."""
    return URLMap.query.filter_by(short=short_id).first() is not None


def _generate_random_short_id(length):
    """Генерирует случайный короткий идентификатор."""
    return ''.join(random.choice(VALID_CHARS) for _ in range(length))


def get_unique_short_id():
    """Генерирует уникальный короткий идентификатор."""
    for length in range(MIN_SHORT_ID_LENGTH, MAX_SHORT_ID_LENGTH + 1):
        attempts = 0
        max_attempts = 100

        while attempts < max_attempts:
            short_id = _generate_random_short_id(length)
            if not _check_short_id_exists(short_id):
                return short_id
            attempts += 1

    timestamp = str(int(time.time()))[-4:]
    random_part = _generate_random_short_id(2)
    fallback_id = timestamp + random_part

    if not _check_short_id_exists(fallback_id):
        return fallback_id

    while True:
        fallback_id += random.choice(VALID_CHARS)
        if not _check_short_id_exists(fallback_id):
            return fallback_id


def _validate_short_id_format(short_id):
    """Проверяет формат короткого идентификатора."""
    if not short_id:
        return True, None

    if len(short_id) > MAX_SHORT_ID_LENGTH:
        return False, ERROR_MESSAGES['invalid_format']

    if short_id.lower() in RESERVED_WORDS:
        return False, ERROR_MESSAGES['already_exists']

    if short_id and (
            not short_id.isalnum() or not all(ord(c) < 128 for c in short_id)
    ):
        return False, ERROR_MESSAGES['invalid_format']

    return True, None


def is_valid_short_id_format(short_id):
    """Проверяет формат короткого идентификатора."""
    is_valid, _ = _validate_short_id_format(short_id)
    return is_valid


def validate_custom_id(custom_id):
    """Валидирует пользовательский вариант короткой ссылки."""
    is_valid, error_message = _validate_short_id_format(custom_id)
    if not is_valid:
        return False, error_message

    if _check_short_id_exists(custom_id):
        return False, ERROR_MESSAGES['already_exists']

    return True, None
