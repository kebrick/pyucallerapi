import json
import re
import logging

import requests
from enum import Enum
from typing import Any

from .decorators import deprecated
from .exception import SetSession, ParamSetException, DataResponseException
from .models import InitCallModel, InitRepeatModel, GetInfoModel, InboundCallWaitingModel, GetServiceModel, \
    GetBalanceModel, GetAccountModel, CheckPhoneModel, ErrorResponseModel, HealthModel


class BaseAPI:
    DEFAULT_TIMEOUT = 60

    class BaseURLuCallerEnum(Enum):
        Http: str = "http://api.ucaller.net/"
        Https: str = "https://api.ucaller.ru/"
        Ip: str = "http://85.193.85.19"
        NoRussianIP: str = "http://api.usa.ucaller.net/"

    class RequestMethod(Enum):
        GET = "Get"
        POST = "Post"

    __error_codes = {
        0: "Ваш IP адрес заблокирован",
        1: "Неверный запрос. Проверьте синтаксис запроса и список используемых параметров (его можно найти на странице с описанием метода).",
        2: "Один из необходимых параметров был не передан или неверен. Проверьте список требуемых параметров и их формат на странице с описанием метода.",
        3: "Неверный номер телефона",
        4: "Работа вашего сервиса отключена в настройках",
        5: "Возникла ошибка при инициализации авторизации",
        9: "Авторизация для этой страны запрещена настройками географии работы в личном кабинете",
        10: "Этот id не существует или у вас нет к нему доступа",
        11: "Авторизация не может быть бесплатно повторена, время истекло",
        12: "Авторизация не может быть бесплатно повторена, лимит исчерпан",
        13: "Ошибочная попытка бесплатной инициализации повторной авторизации",
        18: "Достигнут лимит в 4 исходящих звонка в минуту или 30 вызовов в день для одного номера",
        19: "Подождите 15 секунд перед повторной авторизации на тот же номер",
        20: "Авторизация голосом для этой страны не доступна",
        401: "Аутентификация не удалась. Убедитесь, что Вы используете верную схему aутентификации.",
        405: "Метод не поддерживается.",
        429: "Слишком много запросов в секунду",
        500: "Произошла внутренняя ошибка сервера. Попробуйте повторить запрос позже.",
        1001: "Ваш аккаунт заблокирован",
        1002: "Недостаточно средств на балансе аккаунта",
        1003: "С этого IP запрещено обращаться к API этого сервиса",
        1004: "Сервис заархивирован",
        1005: "Требуется верификация номера телефона в личном кабинете"
    }
    __documentation_url = "https://developer.ucaller.ru/"

    def __init__(
        self,
        service_id: int,
        key: str,
        vesion_api: str = "v1.0",
        session: requests.Session | None = None,
        debug: bool = False,
        base_url: str = None,
        base_headers: dict = None,
        logger: logging.Logger | None = None,
        return_dict: bool = False,
        *args,**kwargs
    ):
        """
        :param service_id:Идентификатор сервиса
        :param key: Секретный ключ вашего сервиса
        :param session: session object
        :param debug: logging dict response
        :param base_url: url server api
        :param base_headers: base header for request
        :param logger: your object Logger
        :param return_dict: return a dictionary instead of models
        """
        assert len(key) == 32, "Длина ключа должна быть 32 символа"

        if session is not None:
            self.__session = session
        else:
            self.__session = requests.Session()

        self.__service_id: int = service_id
        self.__key: str = key
        self.__debug = debug
        self.__return_dict = return_dict
        self.logger = logger if logger is not None else logging.getLogger()

        self.__base_url = self.BaseURLuCallerEnum.Https.value if base_url is None else base_url
        self.__version_api = vesion_api
        self.__headers = {
            'ContentType': 'application/json',
            # 'Accept': 'application/json',
            # 'Content-Encoding': 'utf-8',
        } if base_headers is None else base_headers
        if self.__headers.get("Authorization") is None:
            self.__headers["Authorization"] = f"Bearer {self.__key}.{self.__service_id}"

        self.__session.headers = self.__headers

    @property
    def service_id(self) -> int:
        return self.__service_id

    @property
    def key(self) -> str:
        return self.__key

    @property
    def version_api(self) -> str:
        return self.__version_api

    @property
    def documentation_url(self) -> str:
        """
        Вернёт ссылку на документацию api uCaller
        :return: string with url the documentation api uCaller
        """
        return self.__documentation_url

    @property
    def session_s(self) -> requests.Session:
        """Вывести сессию"""
        return self.__session

    @session_s.setter
    def session_s(self, session: requests.Session = None):
        """Изменение сессии"""
        if session is None:
            raise SetSession(f"Не присвоен объект типа requests.Session")
        else:
            self.__session = session

    @property
    def token(self) -> str:
        return self.__token

    @token.setter
    def token(self, value: str):
        self.__token = value

    @property
    def base_url(self):
        return self.__base_url

    @base_url.setter
    def base_url(self, value: BaseURLuCallerEnum):
        assert isinstance(value, self.BaseURLuCallerEnum), "Передаваемый объект должен быть типа BaseURLuCallerEnum"
        self.__base_url = value.value

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, value: str):
        self.__headers = value

    @property
    def return_dict(self):
        return self.__return_dict

    @return_dict.setter
    def return_dict(self, value: str):
        self.__return_dict = value

    @headers.setter
    def headers(self, value: str):
        self.__return_dict = value

    @property
    def error_codes(self) -> dict:
        return self.__error_codes

    def check_error_code(self, code: int) -> str | None:
        """

        :param code: Код ошибки\
        :return: Вернёт описание либо None
        """
        if code in self.__error_codes.keys():
            return self.__error_codes[code]
        return None

    def _validate_code(self, code: str) -> str:
        """
        Валидация кода
        :param code: код
        :return:
        """
        assert isinstance(code, (str)), "Тип аргумента 'code' не равен 'str'"
        code = re.sub(r'[^\d]', '', code)
        assert len(code) == 4, "код должен состоять из 4 натуральных чисел "
        return code

    def _validate_phone_number(
        self,
        phone: str,
        country_code_format: str | None = None,  # Варианты: "+7", "7", "8", "None"
        re_sub_pattern: str = r'(\d{3})(\d{3})(\d{2})(\d{2})',
        re_sub_repl: str = r'(\1) \2-\3-\4'
    ) -> str | None:
        """
        Форматирует российский номер телефона в единый вид с указанием кода страны.

        Параметры:
            phone (str): Номер телефона в любом формате.
            country_code_format (str): Желаемый формат кода страны ("+7", "7", "8", "None").
            re_sub_pattern (str):
            re_sub_repl (str):
        Возвращает:
            str: Отформатированный номер в зависимости от re_sub_repl.
            None: Если номер некорректный.
        """
        # Удаляем все нецифровые символы
        cleaned = re.sub(r'[^\d]', '', phone)

        # Проверяем длину номера и начало
        if len(cleaned) == 10:
            # Номер без кода страны (допустим, начинается с 9)
            digits = cleaned
        elif len(cleaned) == 11 and cleaned[0] == '8':
            # Номер с 8 в начале → заменяем 8 на 7
            digits = cleaned[1:]
        elif len(cleaned) == 11 and cleaned[0] == '7':
            # Номер с 7 в начале
            digits = cleaned[1:]
        else:
            # Некорректный номер
            raise ValueError("Некорректный номер")

        # Проверяем, что оставшиеся цифры валидны (10 символов, начинаются с 9)
        if not re.fullmatch(r'[89]\d{9}', digits):
            raise ValueError("Некорректный номер")

        # Форматируем код страны в нужный вид
        if country_code_format == "+7":
            prefix = "+7"
        elif country_code_format == "7":
            prefix = "7"
        elif country_code_format == "8":
            prefix = "8"
        elif country_code_format is None:
            prefix = ""
        else:
            raise ValueError("Недопустимый формат кода страны. Допустимые значения: '+7', '7', '8', 'None'")

        # Форматируем номер в удобный вид: (XXX) XXX-XX-XX
        formatted_number = re.sub(
            re_sub_pattern,
            re_sub_repl,
            digits
        )

        return f"{prefix}{formatted_number}"

    def __validate_data(
        self,
        response: requests.Response,
        model_response_data=None,
    ) -> Any:
        if self.__debug:
            try:
                self.logger.debug(
                    f"Входные данные:\n{response.request.url=}\n{response.request.body=}\n{response.request.headers=}\n\nВыходные данные:\n{response.headers=}\n{response.content=}\n\n")
            except Exception as err:
                self.logger.debug(f"{err=}")
        response_data: dict = json.loads(response.content)

        if self.__return_dict:
            return response_data
        if model_response_data is not None:
            match response_data.get("status", None):
                case True:
                    return model_response_data(**response_data)
                case False:
                    return ErrorResponseModel(**response_data)
                case None:
                    try:
                        return model_response_data(**response_data)
                    except Exception as err:
                        raise DataResponseException(f"{response_data} - {err}")

    def _send_request(
        self,
        url: str,
        data: dict | None = None,
        params: dict | None = None,
        method: RequestMethod = RequestMethod.GET,
        model_response_data=None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Any:
        self.logger.info(f"{method=}, {url=}, {data=}, {model_response_data=},")
        match method:
            case self.RequestMethod.GET:
                response = self.session_s.get(f'{self.base_url}{url}', params=params, headers=self.headers,
                                              timeout=timeout)
            case self.RequestMethod.POST:
                assert data is not None, f"При {method=} запросе, data не может быть None"
                # data.update({"key":self.__key,"service_id":self.__service_id})
                response = self.session_s.post(f'{self.base_url}{url}', data=json.dumps(data),
                                               headers=self.headers, timeout=timeout)
            case _:
                raise ValueError(f"Method {method} not supported")

        return self.__validate_data(response, model_response_data)

    def health(
        self,
        timeout=DEFAULT_TIMEOUT,
        *args,**kwargs
    ) -> HealthModel | ErrorResponseModel:
        """
        Этот метод возвращает информацию по сервису.
        URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/getService
        Способ передачи параметров: GET

        :param timeout: timeout request
        :return: pydantic GetServiceModel
        """

        try:
            return self._send_request(
                url="/health",
                model_response_data=HealthModel,
                method=self.RequestMethod.GET,
                timeout=timeout
            )
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Не удалось получить информацию по сервису: \n{err}")
        except ConnectionError as err:
            self.logger.error(f"Ошибка подключения: \n{err}")

class SettingAPI(BaseAPI):
    # GetServiceModel
    def get_service(
        self,
        timeout=BaseAPI.DEFAULT_TIMEOUT,
        *args,**kwargs
    ) -> GetServiceModel | ErrorResponseModel:
        """
        Этот метод возвращает информацию по сервису.
        URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/getService
        Способ передачи параметров: GET

        :param timeout: timeout request
        :return: pydantic GetServiceModel
        """

        try:
            return self._send_request(
                url=f"{self.version_api}/getService",
                model_response_data=GetServiceModel,
                method=self.RequestMethod.GET,
                timeout=timeout
            )
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Не удалось получить информацию по сервису: \n{err}")
        except ConnectionError as err:
            self.logger.error(f"Ошибка подключения: \n{err}")
    def get_balance(
        self,
        timeout=BaseAPI.DEFAULT_TIMEOUT,
        *args,**kwargs
    ) -> GetBalanceModel | ErrorResponseModel:
        """
        Этот метод возвращает информацию по балансу.
        URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/getBalance
        Способ передачи параметров: GET

        :param timeout: timeout request
        :return: pydantic GetBalanceModel
        """

        try:
            return self._send_request(
                url=f"{self.version_api}/getBalance",
                model_response_data=GetBalanceModel,
                method=self.RequestMethod.GET,
                timeout=timeout
            )
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Не удалось получить информацию по сервису: \n{err}")
        except ConnectionError as err:
            self.logger.error(f"Ошибка подключения: \n{err}")
    def get_account(
        self,
        timeout=BaseAPI.DEFAULT_TIMEOUT,
        *args,**kwargs
    ) -> GetAccountModel | ErrorResponseModel:
        """
        Этот метод возвращает информацию по балансу.
        URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/getAccount
        Способ передачи параметров: GET

        :param timeout: timeout request
        :return: pydantic GetAccountModel
        """

        try:
            return self._send_request(
                url=f"{self.version_api}/getAccount",
                model_response_data=GetAccountModel,
                method=self.RequestMethod.GET,
                timeout=timeout
            )
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Не удалось получить информацию по сервису: \n{err}")
        except ConnectionError as err:
            self.logger.error(f"Ошибка подключения: \n{err}")

class CallAPI(BaseAPI):
    def init_call(
        self,
        phone: str,
        code: str ,
        client: str = None,
        unique: str = None,
        voice: bool = False,
        mix: bool = False,
        timeout=BaseAPI.DEFAULT_TIMEOUT,
        *args,**kwargs
    ) -> InitCallModel | ErrorResponseModel:
        """
		Данный метод позволяет инициализировать авторизацию для пользователя вашего приложения.
		URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/initCall
		Способ передачи параметров: GET

		:param phone: string phone number
		:param code: string == 4 characters
		:param client: Набор символов До 64 символов
		:param unique: Набор символов До 64 символов
		:param voice: voice request, default = False
        :param mix:
		:param timeout: timeout request, default = 60 sec
		:return: pydantic InitCallModel
        """
        phone = self._validate_phone_number(phone, country_code_format="+7", re_sub_repl=r'\1\2\3\4')
        code = self._validate_code(code)
        data = {
            "phone": phone,
            "code": code,
        }
        if voice: data['voice'] = voice
        if mix: data['mix'] = mix
        if client is not None:
            if not isinstance(client, str): client = str(client)
            if len(client) > 64: raise ParamSetException("Длина аргумента client должна быть до 64 символа")
            data["client"] = client

        if unique is not None:
            if not isinstance(unique, str): unique = str(unique)
            if len(unique) > 64: raise ParamSetException("Длина аргумента client должна быть до 64 символа")
            data["unique"] = unique

        try:

            return self._send_request(
                url=f"{self.version_api}/initCall/",
                params=data,
                model_response_data=InitCallModel,
                method=self.RequestMethod.GET,
                timeout=timeout
            )
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Не удалось получить инициализировать авторизацию: \n{err}")
        except ConnectionError as err:
            self.logger.error(f"Ошибка подключения: \n{err}")


    @deprecated("Метод больше не поддерживается")
    def init_repeat(
        self, uid: str,
        timeout=BaseAPI.DEFAULT_TIMEOUT,
        *args,**kwargs
    ) -> InitRepeatModel | ErrorResponseModel:
        """
		В случае, если ваш пользователь не получает звонок инициализированный методом initCall, вы можете два раза и
		совершенно бесплатно инициализировать повторную авторизацию по uCaller ID, который вы получаете в ответе
		метода initCall. Повторную авторизацию можно запросить только в течение пяти минут с момента выполнения
		основной авторизации методом initCall. Все данные, например `code` или `phone`, совпадают с теми же,
		которые были переданы в первом запросе initCall.

		URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/initRepeat

		Способ передачи параметров: GET

		:param uid: Идентификатор ucaller_id из метода initCall
		:param timeout: timeout request
		:return: pydantic InitRepeatModel
        """

        try:
            return self._send_request(
                url=f"{self.version_api}/initRepeat",
                params={"uid": uid, },
                model_response_data=InitCallModel,
                method=self.RequestMethod.GET,
                timeout=timeout
            )
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Не удалось инициализировать повторную авторизацию : \n{err}")
        except ConnectionError as err:
            self.logger.error(f"Ошибка подключения: \n{err}")
    def get_info(
        self, uid: int,
        timeout=BaseAPI.DEFAULT_TIMEOUT,
        *args,**kwargs
    ) -> GetInfoModel | ErrorResponseModel:
        """
        Этот метод возвращает развернутую информацию по уже осуществленному uCaller ID.
		URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/getInfo
		Способ передачи параметров: GET

		:param uid: Идентификатор ucaller_id из метода initCall
		:param timeout: timeout request
		:return: pydantic GetInfoModel
        """

        try:
            return self._send_request(
                url=f"{self.version_api}/getInfo",
                params={"uid": uid, },
                model_response_data=GetInfoModel,
                method=self.RequestMethod.GET,
                timeout=timeout
            )
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Не удалось инициализировать повторную авторизацию : \n{err}")
        except ConnectionError as err:
            self.logger.error(f"Ошибка подключения: \n{err}")
    def inbound_call_waiting(
        self,
        phone: str,
        callback_url: str,
        timeout=BaseAPI.DEFAULT_TIMEOUT,
        *args,**kwargs
    ) -> InboundCallWaitingModel | ErrorResponseModel:
        """
        Метод позволяет организовать верификацию номера телефона по входящему звонку
		URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/inboundCallWaiting
		Способ передачи параметров: GET

        :param phone:Номер телефона пользователя, которому будет совершен звонок с авторизацией, цифровой формат номера E.164
        :param callback_url: Ссылка для оповещения (web-hook) о вызове на номер.
		:param timeout: timeout request
		:return: pydantic InboundCallWaitingModel
        """
        phone = self._validate_phone_number(phone, country_code_format="+7", re_sub_repl=r'\1\2\3\4')

        try:
            return self._send_request(
                url=f"{self.version_api}/inboundCallWaiting/",
                params={"phone": phone, "callback_url": callback_url},
                model_response_data=InboundCallWaitingModel,
                method=self.RequestMethod.GET,
                timeout=timeout
            )
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Не удалось организовать верификацию номера телефона по входящему звонку: \n{err}")
        except ConnectionError as err:
            self.logger.error(f"Ошибка подключения: \n{err}")
    def check_phone(
        self,
        phone: str,
        timeout=BaseAPI.DEFAULT_TIMEOUT,
        *args,**kwargs
    ) -> CheckPhoneModel | ErrorResponseModel:
        """
        Метод позволяет организовать верификацию номера телефона по входящему звонку
		URL обращения для инициализации метода: https://api.ucaller.ru/v1.0/checkPhone
		Способ передачи параметров: GET

        :param phone:Номер телефона
		:param timeout: timeout request
		:return: pydantic CheckPhoneModel
        """
        phone = self._validate_phone_number(phone, country_code_format="+7", re_sub_repl=r'\1\2\3\4')

        try:
            return self._send_request(
                url=f"{self.version_api}/checkPhone",
                params={"phone": phone, },
                model_response_data=CheckPhoneModel,
                method=self.RequestMethod.GET,
                timeout=timeout
            )
        except requests.exceptions.RequestException as err:
            self.logger.error(f"Не удалось организовать верификацию номера телефона по входящему звонку: \n{err}")
        except ConnectionError as err:
            self.logger.error(f"Ошибка подключения: \n{err}")

class APIUCaller(SettingAPI, CallAPI):
    pass


class UCallerAPI(SettingAPI, CallAPI):
    pass
