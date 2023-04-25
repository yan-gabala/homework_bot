class TelegramSendError(Exception):
    """Сообщение в чат не отправлено."""

    pass


class GetAPIError(Exception):
    """Неверный ответ от сервера."""

    pass


class StatusNotOKError(Exception):
    """Запрос не возвращает статус 200."""

    pass


class CheckResponseError(Exception):
    """Неверный ответ для функции check_response()."""

    pass
