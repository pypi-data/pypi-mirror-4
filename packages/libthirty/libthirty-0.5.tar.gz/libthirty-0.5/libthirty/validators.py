from docar.exceptions import ValidationError
import re


def naming(value):
    p = re.compile('^[a-z0-9_]+$')
    if not p.match(value):
        raise ValidationError("String invalid. May contain [a-z0-9_].")


def naming_with_dashes(value):
    p = re.compile('^[A-Za-z0-9_-]+$')
    if not p.match(value):
        raise ValidationError("String invalid. May contain [A-Za-z0-9_-].")


def max_25_chars(value):
    """Validate that valuew is not longer than 25 characters."""
    if len(value) >= 25:
        raise ValidationError(
                "String too long. A maximum of 25 characters allowed")
