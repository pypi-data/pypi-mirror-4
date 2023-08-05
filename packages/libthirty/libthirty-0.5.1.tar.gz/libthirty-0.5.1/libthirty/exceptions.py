class HttpError(Exception):
    """If there is an error during the HTTP communication, this exception is
    raised."""
    pass


class HttpReturnError(Exception):
    """In case the HTTP requests returns a 40[0-4] or a 50[0-4] status code,
    raise this exception."""
    pass
