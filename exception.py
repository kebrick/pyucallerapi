class uCallerException(Exception):
	pass


class GetException(uCallerException):
	"""Basic exception for errors thrown on get request."""

	def __init__(self, name_class, name_method, message):
		super().__init__(f"Class \"{name_class}\": Method \"{name_method}\" - {message}")


class SetSession(uCallerException):
	"""Base exception for errors caused within a get couriers."""

	def __init__(self, name_class, name_method, message):
		super().__init__(f"Class {name_class}: Method - {name_method} - {message}")


class SetServiceId(uCallerException):
	"""Base exception for errors caused within a get couriers."""

	def __init__(self, name_class, name_method, message):
		super().__init__(f"Class {name_class}: Method - {name_method} - {message}")


class SetKey(uCallerException):
	"""Base exception for errors caused within a get couriers."""

	def __init__(self, name_class, name_method, message, exit_now: int = None):
		super().__init__(f"Class {name_class}: Method - {name_method} - {message}")
		if exit_now is not None:
			exit(exit_now)


class ParamSetException(uCallerException):
	""""""

	def __init__(self, name_class, name_method, message):
		super().__init__(f"Class {name_class}: Method - {name_method} - {message}")
