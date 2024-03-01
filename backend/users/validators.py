import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if re.search(r'^[\w.@+-]+\Z', value) is None:
        raise ValidationError(
            ('Не допустимые символы в имени пользователя'),
            params={'value': value},
        )
    return value
