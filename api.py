from re import match
import requests

from .exception import SetSession, SetServiceId, SetKey, ParamSetException, GetException


class BaseUCaller:
	__REGEX_PHONE = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
	__ORG_URL = "https://ucaller.ru/"
	__DOC_URL = "https://ucaller.ru/doc"
	__ERROR_UCALLER = {
		"0": "Ваш IP адрес заблокирован",
		"1": "Не переданы какие-либо требуемые GET параметры",
		"2": "Неверная комбинация GET параметров `service_id` и `key`",
		"3": "Возникла ошибка при инициализации авторизации (неверный номер телефона или тех. работы)",
		"4": "Работа вашего сервиса отключена в настройках",
		"5": "[Тестовый режим] Вы не прошли верификацию номера телефона в личном кабинете",
		"6": "[Тестовый режим] Баланс бесплатных тестовых авторизаций исчерпан",
		"7": "[Тестовый режим] Переданный GET параметр `phone` не разрешен (на него не пройдена верификация)",
		"8": "Проверьте максимально допустимую длину передаваемых значений",
		"9": "Авторизация для этой страны запрещена настройками географии работы в личном кабинете",
		"10": "Этот uCaller id не существует или у вас нет к нему доступа",
		"11": "Авторизация не может быть бесплатно повторена, время истекло",
		"12": "Авторизация не может быть бесплатно повторена, лимит исчерпан",
		"13": "Ошибочная попытка бесплатной инициализации повторной авторизации",
		"14": "[Widget] Неверный формат переданного ucaller-response",
		"15": "[Widget] Такого ответа ucaller-response не существует",
		"16": "[Widget] Виджет отключен в настройках",
		"17": "[Widget] Ключи виджета нельзя использовать для API Classic",
		"18": "Достигнут лимит в 4 исходящих звонка в минуту или 15 вызовов в день для одного номера",
		"1000": "Этот метод API временно недоступен",
		"1001": "Ваш аккаунт заблокирован",
		"1002": "Недостаточно средств на балансе аккаунта",
		"1003": "С этого IP запрещено обращаться к API этого сервиса",
		"1004": "Сервис заархивирован",
	}
	def __init__(
		self,
		service_id: int,
		key: str,
		session: requests.Session = None
	):
		"""

		:param service_id: ID of the service you created
		:param key: string == 32 characters
		:param session: A Requests session. default = None
		"""
		self.__service_id = service_id

		if len(key) > 32:
			raise SetKey(
				self.__class__.__qualname__,
				self.service_id.__name__,
				f"[ERROR] длина key > 32 символо: len(key) = {len(key)}",
				100,
			)
		self.__key = key

		if session is not None:
			self.__session = session
		else:
			self.__session = requests.Session()
			self.__session.headers = {
				'ContentType': 'application/json',
				'Accept': 'application/json',
				'Content-Encoding': 'utf-8'
			}

		self.__base_url = "https://api.ucaller.ru/"
		self.__version_api = "v1.0"

	def __doc_uCaller__(self) -> str:
		"""
		Вернёт ссылку на документацию api uCaller
		:return: string with url the documentation api uCaller
		"""
		return self.__DOC_URL

	def __service_url__(self):
		"""
		Вернёт ссылку на сайт uCaller
		:return: string with url the site uCaller
		"""
		return self.__ORG_URL

	@property
	def error_codes(self) -> dict:
		"""
		Вернёт словарь код:значение
		:return: dict code:value
		"""
		return self.__ERROR_UCALLER

	@property
	def base_url(self) -> str:
		return self.__base_url

	@base_url.setter
	def base_url(self, url: str):
		self.__base_url = url

	@property
	def version_api(self) -> str:
		return self.__version_api

	@version_api.setter
	def version_api(self, version: str):
		self.__version_api = version

	@property
	def regex_phone(self) -> str:
		return self.__REGEX_PHONE

	@regex_phone.setter
	def regex_phone(self, regex: str):
		self.__REGEX_PHONE = regex

	@property
	def service_id(self) -> int:
		return self.__service_id

	@service_id.setter
	def service_id(self, service_id: int):
		if service_id == self.__service_id:
			raise SetServiceId(
				self.__class__.__qualname__,
				self.service_id.__name__,
				f"[ERROR] id сервиса совпадает с изменяемым id")
		else:
			self.__service_id = service_id

	@property
	def key(self) -> str:
		"""
		Cекретный ключ

		:return: string == 32 characters
		"""
		return self.__key

	@key.setter
	def key(self, key: str):
		"""
		Изменение секретного ключа

		:param key: string == 32 characters
		"""
		if len(key) > 32:
			raise SetKey(
				self.__class__.__qualname__,
				self.service_id.__name__,
				f"[ERROR] длина key > 32 символо: len(key) = {len(key)}",
			)
		else:
			self.__key = key

	@property
	def session(self) -> requests.Session:
		"""
		A Requests session

		:return: object requests.Session
		"""
		return self.__session

	@session.setter
	def session(self, session: requests.Session = None):
		"""
		Изменение сессии

		:param session: A Requests session
		"""
		if session is None:
			raise SetSession(
				self.__class__.__qualname__,
				self.session.__name__,
				f"[ERROR] Не присвоен объект типа requests.Session")
		else:
			self.__session = session

	@classmethod
	def check_phone(cls, phone: str):
		if match(cls.__REGEX_PHONE, phone):
			return True
		return False

	@classmethod
	def change_phone(cls, phone):
		if phone[0] == "+" and phone[1] == "7":
			phone = phone[1:]
		elif phone[0] == "7":
			phone = phone
		elif phone[0] == "8":
			phone = f"7{phone[1:]}"
		else:
			phone = f"7{phone[1:]}"
		return phone

	def check_error_code(self, error_code):
		"""

		:param error_code: Код ошибки
		:return: Вернёт описание либо None
		"""
		if str(error_code) in self.__ERROR_UCALLER.keys():
			return self.__ERROR_UCALLER.get(str(error_code), None)
		return None


class APIUCaller(BaseUCaller):

	def init_call(self, phone: str, code, client: str = None, unique: str = None, timeout=60) -> dict:
		"""
		Данный метод позволяет инициализировать авторизацию для пользователя вашего приложения.

		URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/initCall

		Способ передачи параметров: GET

		:param phone: string phone number
		:param code: string == 4 characters
		:param client: Набор символов До 64 символов
		:param unique: Набор символов До 64 символов
		:param timeout: timeout request, default = 60 sec
		:return: смотрите  APIExampleResponse.example_response_init_сall
		"""
		# /api/0/orders/add?access_token={accessToken}&request_timeout={requestTimeout}
		if not self.check_phone(phone=phone):
			raise ParamSetException(
				self.__class__.__qualname__,
				self.init_call.__name__,
				f"[ERROR] неверный формат телефона \n+79999999999\n79999999999\n9999999999"
			)
		if len(code) > 4 or len(code) < 4:
			raise ParamSetException(
				self.__class__.__qualname__,
				self.init_call.__name__,
				f"[ERROR] Кол-во символов параметра \"code\", больше либо меньше 4"
			)
		if client is not None and len(client) > 64:
			raise ParamSetException(
				self.__class__.__qualname__,
				self.init_call.__name__,
				f"[ERROR] Кол-во символов параметра \"client\", больше 64"
			)
		if unique is not None and len(unique) > 64:
			raise ParamSetException(
				self.__class__.__qualname__,
				self.init_call.__name__,
				f"[ERROR] Кол-во символов параметра \"unique\", больше 64"
			)
		phone = self.change_phone(phone)
		try:

			result = self.session.get(
				f"{self.base_url}{self.version_api}/initCall?service_id={self.service_id}&key={self.key}&phone={phone}" +
				f"&code={code}{f'&client={client}' if client is not None else ''}" +
				f"{f'&unique={unique}' if unique is not None else ''}",
				timeout=timeout,
			)
			return result.json()

		except requests.exceptions.RequestException as err:
			raise GetException(
				self.__class__.__qualname__,
				self.init_call.__name__,
				f"[ERROR] Не удалось инициализировать авторизацию\n{err}"
			)

	def init_repeat(self, uid: str, timeout=60) -> dict:
		"""
		В случае, если ваш пользователь не получает звонок инициализированный методом initCall, вы можете два раза и
		совершенно бесплатно инициализировать повторную авторизацию по uCaller ID, который вы получаете в ответе
		метода initCall. Повторную авторизацию можно запросить только в течение пяти минут с момента выполнения
		основной авторизации методом initCall. Все данные, например `code` или `phone`, совпадают с теми же,
		которые были переданы в первом запросе initCall.

		URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/initRepeat

		Способ передачи параметров: GET

		:param uid:
		:param timeout: timeout request
		:return: смотрите APIExampleResponse.example_response_get_repeat
		"""

		try:
			result = self.session.get(
				f"{self.base_url}{self.version_api}/initRepeat?service_id={self.service_id}&key={self.key}&uid={uid}",
				timeout=timeout
			)
			return result.json()

		except requests.exceptions.RequestException as err:
			raise GetException(
				self.__class__.__qualname__,
				self.init_repeat.__name__,
				f"[ERROR] Не удалось повторить авторизацию\n{err}"
			)

	def get_info(self, uid: str, timeout=60) -> dict:
		"""
		Этот метод возвращает развернутую информацию по уже осуществленному uCaller ID.

		:param uid: uCaller ID переданный в ответе init_сall
		:param timeout: timeout request
		:return: смотрите APIExampleResponse.example_response_get_info
		"""

		try:
			result = self.session.get(
				f"{self.base_url}{self.version_api}/getInfo?service_id={self.service_id}&key={self.key}&uid={uid}",
				timeout=timeout
			)
			return result.json()

		except requests.exceptions.RequestException as err:
			raise GetException(
				self.__class__.__qualname__,
				self.get_info.__name__,
				f"[ERROR] Не удалось получить развернутую информацию по уже осуществленному uCaller ID\n{err}"
			)

	def get_balance(self, timeout=60) -> dict:
		"""
		Этот метод возвращает информацию по остаточному балансу.

		URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/getBalance

		Способ передачи параметров: GET

		:param timeout: timeout request
		:return: смотрите APIExampleResponse.example_response_get_balance
		"""

		try:
			result = self.session.get(
				f"{self.base_url}{self.version_api}/getBalance?service_id={self.service_id}&key={self.key}",
				timeout=timeout
			)
			return result.json()

		except requests.exceptions.RequestException as err:
			raise GetException(
				self.__class__.__qualname__,
				self.get_balance.__name__,
				f"[ERROR] Не удалось получить информацию по остаточному балансу\n{err}"
			)

	def get_service(self, timeout=60) -> dict:
		"""
		Этот метод возвращает информацию по сервису.

		URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/getService

		Способ передачи параметров: GET

		:param timeout: timeout request
		:return: смотрите APIExampleResponse.example_response_get_service
		"""

		try:
			result = self.session.get(
				f"{self.base_url}{self.version_api}/getService?service_id={self.service_id}&key={self.key}",
				timeout=timeout
			)
			return result.json()

		except requests.exceptions.RequestException as err:
			raise GetException(
				self.__class__.__qualname__,
				self.get_service.__name__,
				f"[ERROR] Не удалось получить информацию по остаточному балансу\n{err}"
			)


class APIExampleResponse:
	# noinspection PyMethodMayBeStatic
	def example_response_get_info(self) -> dict:
		"""
		Вернёт пример ответа метода get_info
		:return: will return an example of the response of the 'get_info' method
		"""
		return {
			"status": True,  # true в случае успеха, false в случае неудачи
			"ucaller_id": 103000,  # запрошенный uCaller ID
			"init_time": 1556617525,  # время, когда была инициализирована авторизация
			"call_status": -1,
			# Статус звонка, -1 = информация проверяется (от 1 сек до 1 минуты), 0 = дозвониться не удалось, 1 = звонок осуществлен
			"is_repeated": False,
			# является ли этот uCaller ID повтором (initRepeat), если да, будет добавлен first_ucaller_id с первым uCaller ID этой цепочки
			"repeatable": False,  # возможно ли инициализировать бесплатные повторы (initRepeat)
			"repeat_times": 2,  # Появляется в случае repeatable: true, говорит о количестве возможных повторов
			"repeated_ucaller_ids": [103001, 103002],  # цепочка  uCaller ID инициализированных повторов (initRepeat)
			"unique": "f32d7ab0-2695-44ee-a20c-a34262a06b90",  # ключ идемпотентности (если был передан)
			"client": "nickname",  # идентификатор пользователя переданный клиентом (если был передан)
			"phone": 79991234567,  # номер телефона пользователя, куда мы совершали звонок
			"code": 7777,  # код авторизации
			"country_code": "RU",  # ISO код страны пользователя
			"country_image": "https://static.ucaller.ru/flag/ru.svg",  # изображение флага страны пользователя
			"phone_info": [  # информация по телефону, информация может отличаться от примера
				{
					"operator": "МТС",  # Оператор связи
					"region": "Республика Татарстан",  # регион субъеккта Российской федерации
					"mnp": "Мегафон"  # Если у номера был сменен оператор - MNP покажет нового оператора
				}
			],
			"cost": 0.3  # сколько стоила эта авторизация клиенту
		}

	# noinspection PyMethodMayBeStatic
	def example_response_init_repeat(self) -> dict:
		"""
		Вернёт пример ответа метода init_repeat
		:return: will return an example of the response of the 'init_repeat' method
		"""
		return {
			"status": True,
			"ucaller_id": 103001,
			"phone": 79991234567,
			"code": 7777,
			"client": "nickname",
			"unique_request_id": "f32d7ab0-2695-44ee-a20c-a34262a06b90",
			"exists": True,
			"free_repeated": True,  # показывает, что осуществлена повторная авторизация
		}

	# noinspection PyMethodMayBeStatic
	def example_response_init_call(self) -> dict:
		"""
		Вернёт пример ответа метода init_call
		:return: will return an example of the response of the 'init_call' method
		"""
		return {
			"status": True,  # True в случае успеха, false в случае неудачи
			"ucaller_id": 103000,
			# уникальный ID в системе uCaller, который позволит проверять статус и инициализировать метод initRepeat
			"phone": 79991234567,  # номер телефона, куда мы совершили звонок
			"code": 7777,  # код, который будет последними цифрами в номере телефона
			"client": "nickname",  # идентификатор пользователя переданный клиентом
			"unique_request_id": "f32d7ab0-2695-44ee-a20c-a34262a06b90",
			# появляется только если вами был передан параметр `unique`
			"exists": True
			# появляется при переданном параметре `unique`, если такой запрос уже был инициализирован ранее
		}

	# noinspection PyMethodMayBeStatic
	def example_response_get_balance(self) -> dict:
		"""
		Вернёт пример ответа метода get_balance
		:return: will return an example of the response of the 'get_balance' method
		"""
		return {
			"status": True,  # True в случае успеха, false в случае неудачи
			"rub_balance": 84.6,  # Остаточный баланс на рублевом счете аккаунта
			"bonus_balance": 0,  # Остаточный бонусный баланс
			"tariff": "startup",  # Кодовое значение вашего тарифного плана
			"tariff_name": "Старт-ап"  # Название тарифного плана
		}

	# noinspection PyMethodMayBeStatic
	def example_response_get_service(self) -> dict:
		"""
		Вернёт пример ответа метода get_service
		:return: will return an example of the response of the 'get_service' method
		"""
		return {
			"status": True,  # true в случае успеха, false в случае неудачи
			"service_status": 1692,  # ID сервиса
			"name": "ВКонтакте",  # Название сервиса
			"creation_time": 1556064401,  # Время создания сервиса в unix формате
			"last_request": 1556707453,  # Время последнего не кэшированного обращения к API сервиса в unix формате
			"owner": "example@ucaller.ru",  # E-mail адрес владельца сервиса
			"use_direction": "ВКонтакте приложение",  # Информация о том, где будет использоваться сервис
			"now_test": True,  # Состояние тестового режима на текущий момент
			"test_info": {
				"test_requests": 89,  # Оставшееся количество бесплатных тестовых обращений
				"verified_phone": 79991234567  # Верифицированный номер телефона для тестовых обращений
			}
		}



