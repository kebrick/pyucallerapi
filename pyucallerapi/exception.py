import inspect


class uCallerException(Exception):
    __slots__ = ()


class GetException(uCallerException):
    def __init__(self, message: str):
        frame = inspect.currentframe().f_back
        # Получаем self (если есть) для определения класса
        self_obj = frame.f_locals.get('self', None)
        class_name = self_obj.__class__.__qualname__ if self_obj else None
        method_name = frame.f_code.co_name

        if class_name:
            error_msg = f"Class {class_name}: Method - {method_name} - {message}"
        else:
            error_msg = f"Function - {method_name} - {message}"

        super().__init__(error_msg)

class DataResponseException(uCallerException):
    def __init__(self, message: str):
        frame = inspect.currentframe().f_back
        # Получаем self (если есть) для определения класса
        self_obj = frame.f_locals.get('self', None)
        class_name = self_obj.__class__.__qualname__ if self_obj else None
        method_name = frame.f_code.co_name

        if class_name:
            error_msg = f"Class {class_name}: Method - {method_name} - {message}"
        else:
            error_msg = f"Function - {method_name} - {message}"

        super().__init__(error_msg)

class SetSession(uCallerException):
    def __init__(self, message: str):
        frame = inspect.currentframe().f_back
        # Получаем self (если есть) для определения класса
        self_obj = frame.f_locals.get('self', None)
        class_name = self_obj.__class__.__qualname__ if self_obj else None
        method_name = frame.f_code.co_name

        if class_name:
            error_msg = f"Class {class_name}: Method - {method_name} - {message}"
        else:
            error_msg = f"Function - {method_name} - {message}"

        super().__init__(error_msg)

class SetServiceId(uCallerException):
    def __init__(self, message: str):
        frame = inspect.currentframe().f_back
        # Получаем self (если есть) для определения класса
        self_obj = frame.f_locals.get('self', None)
        class_name = self_obj.__class__.__qualname__ if self_obj else None
        method_name = frame.f_code.co_name

        if class_name:
            error_msg = f"Class {class_name}: Method - {method_name} - {message}"
        else:
            error_msg = f"Function - {method_name} - {message}"

        super().__init__(error_msg)

class SetKey(uCallerException):
    def __init__(self, message: str):
        frame = inspect.currentframe().f_back
        # Получаем self (если есть) для определения класса
        self_obj = frame.f_locals.get('self', None)
        class_name = self_obj.__class__.__qualname__ if self_obj else None
        method_name = frame.f_code.co_name

        if class_name:
            error_msg = f"Class {class_name}: Method - {method_name} - {message}"
        else:
            error_msg = f"Function - {method_name} - {message}"

        super().__init__(error_msg)

class ParamSetException(uCallerException):
    def __init__(self, message: str):
        frame = inspect.currentframe().f_back
        # Получаем self (если есть) для определения класса
        self_obj = frame.f_locals.get('self', None)
        class_name = self_obj.__class__.__qualname__ if self_obj else None
        method_name = frame.f_code.co_name

        if class_name:
            error_msg = f"Class {class_name}: Method - {method_name} - {message}"
        else:
            error_msg = f"Function - {method_name} - {message}"

        super().__init__(error_msg)







