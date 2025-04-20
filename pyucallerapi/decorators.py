import warnings
from functools import wraps




def deprecated(message: str | None = None, version: str | None = None, ):
    """
    Декоратор для пометки функций как устаревших с указанием версии.

    Args:
        version (str): Версия, в которой функция будет удалена.
        message (str): Кастомное сообщение.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            default_msg = f"Функция {func.__name__} устарела."
            if version is not None:
                default_msg += f" Будет удалена в версии {version}."
            warn_msg = message or default_msg
            warnings.warn(warn_msg, DeprecationWarning, stacklevel=1)
            return func(*args, **kwargs)

        return wrapper

    return decorator
