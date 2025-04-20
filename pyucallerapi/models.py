from datetime import datetime
from enum import Enum
from typing import Union, Literal, Annotated

from pydantic import BaseModel, Field, constr


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class BaseCallDataModel(BaseModel):
    status: Literal[True] = Field(True, frozen=True)  # Фиксированное значение True
    ucaller_id: int
    phone: str
    code: str | None = None
    client: str | None = None
    unique_request_id: str | None = None

    class Config:
        json_schema_extra = {
            "status": True,
            "ucaller_id": 103000,
            "phone": "7900***1010",
            "code": "1000",
            "client": "nickname",
            "unique_request_id": "f32d7ab0-2695-44ee-a20c-a34262a06b90",

        }


class ErrorResponseModel(BaseModel):
    status: Literal[False] = Field(False, frozen=True)
    error: str
    code: int

    class Config:
        json_schema_extra = {"status": False, "error": "Error", "code": 500}


class InitCallModel(BaseCallDataModel):
    exists: bool | None = None

    class Config:
        # Для игнорирования deprecated полей при валидации
        extra = "ignore"
        json_schema_extra = {
            "example": {
                "status": True,
                "ucaller_id": 103000,
                "phone": "7900***1010",
                "code": "1000",
                "client": "nickname",
                "unique_request_id": "f32d7ab0-2695-44ee-a20c-a34262a06b90",
                "exists": True
            }
        }


class InitRepeatModel(BaseCallDataModel):
    exists: bool
    free_repeated: bool

    class Config:
        # Для игнорирования deprecated полей при валидации
        extra = "ignore"
        json_schema_extra = {
            "status": True,
            "ucaller_id": 103000,
            "phone": "7900***1010",
            "code": "1000",
            "client": "nickname",
            "unique_request_id": "f32d7ab0-2695-44ee-a20c-a34262a06b90",
            "exists": True,
            "free_repeated": True

        }


class PhoneInfo(BaseModel):
    """Информация о номере телефона"""
    operator: str | None = None
    region: str | None = None
    mnp: str | None = None


class GetInfoModel(BaseCallDataModel):
    """Модель ответа от uCaller API"""
    init_time: int
    call_status: int  # -1=проверка, 0=не удалось, 1=успешно
    is_repeated: bool | None = Field(None, deprecated=True)  # deprecated
    first_ucaller_id: int | None = Field(None, deprecated=True)  # deprecated
    repeatable: bool | None = Field(None, deprecated=True)  # deprecated
    repeat_times: int | None = Field(None, deprecated=True)  # deprecated
    repeated_ucaller_ids: list[int] | None = Field(None, deprecated=True)  # deprecated
    country_code: str
    phone_info: list[PhoneInfo] | None = None
    cost: float
    balance: float

    class Config:
        # Для игнорирования deprecated полей при валидации
        extra = "ignore"
        json_schema_extra = {
            "status": True,
            "ucaller_id": 103000,
            "init_time": 1556617525,
            "call_status": -1,
            "is_repeated": False,
            "first_ucaller_id": 102999,
            "repeatable": False,
            "repeat_times": 2,
            "repeated_ucaller_ids": [103001, 103002],
            "unique": "f32d7ab0-2695-44ee-a20c-a34262a06b90",
            "client": "nickname",
            "phone": "7900***1010",
            "code": "0010",
            "country_code": "RU",
            "phone_info": [{
                "operator": "МТС",
                "region": "Республика Татарстан",
                "mnp": "Мегафон"
            }],
            "cost": 0.3,
            "balance": 568.12

        }


class InboundCallWaitingModel(BaseCallDataModel):
    confirmation_number: str

    class Config:
        json_schema_extra = {
            "status": True,
            "ucaller_id": 103000,
            "phone": "7900***1010",
            "confirmation_number": "79001000011",
        }


class UcallerWebhookModel(BaseModel):
    """
    Модель для валидации входящего webhook от uCaller.
    Используется при звонке на номер для верификации.
    """
    callId: str = Field(..., description="Уникальный ID в системе uCaller")
    callbackLink: str = Field(..., description="URL для callback-ответа")
    clientNumber: str = Field(..., description="Номер для верификации")
    confirmationNumber: str = Field(..., description="Номер для подтверждения")
    isMnp: bool = Field(..., description="Признак портированного номера")
    operatorName: str | None = Field(
        None,
        description="Оператор связи (пусто, если isMnp=False)"
    )
    operatorNameMnp: str | None = Field(
        None,
        description="Оператор, куда портирован номер (пусто, если isMnp=False)"
    )
    regionName: str = Field(..., description="Регион номера")

    class Config:
        # Пример данных для документации
        json_schema_extra = {
            "callId": "10300",
            "callbackLink": "https://example.com/callback",
            "clientNumber": "79001000010",
            "confirmationNumber": "79001000011",
            "isMnp": True,
            "operatorName": "ООО Скартел",
            "operatorNameMnp": "ВымпелКом ПАО",
            "regionName": "Пермский край"

        }


class GetServiceModel(BaseModel):
    service_status: int
    name: str
    creation_time: int
    last_request: int
    owner: str
    use_direction: str

    class Config:
        json_schema_extra = {
            "status": True,
            "service_status": 1692,
            "name": "ВКонтакте",
            "creation_time": 1556064401,
            "last_request": 1556707453,
            "owner": "example@ucaller.ru",
            "use_direction": "ВКонтакте приложение"
        }


class GetBalanceModel(BaseModel):
    status: bool
    rub_balance: float
    tariff: str
    tariff_name: str

    class Config:
        json_schema_extra = {
            "status": True,
            "rub_balance": 84.6,
            "tariff": "uni",
            "tariff_name": "Единый"

        }


class UserLog(BaseModel):
    action: str
    user_agent: str
    ip: str
    created: int  # Unix Timestamp

    # Дополнительное свойство для удобства (необязательно)
    @property
    def created_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.created)


class GetAccountModel(BaseModel):
    id: int
    telegram_id: int
    two_auth: bool
    email: str
    logs: list[UserLog]
    updated: int  # Unix Timestamp
    created: int  # Unix Timestamp

    # Дополнительные свойства для удобства (необязательно)
    @property
    def updated_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.updated)

    @property
    def created_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.created)

    class Config:
        json_schema_extra = {
            "id": 1,
            "telegram_id": 123456789,
            "two_auth": True,
            "email": "email@gmail.com",
            "logs": [{
                "action": "смена пароля",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
                "ip": "127.0.0.1",
                "created": 1636552838
            }],
            "updated": 1638857962,
            "created": 1636552838
        }


class CheckPhoneModel(BaseModel):
    source: str = Field(..., description="Исходный телефон одной строкой")
    error: str | None = Field(None, description="Ошибка (если номер невалидный)")
    mobile: int = Field(..., description="Тип номера: мобильный=1, не мобильный=0")
    phone: int = Field(..., description="Номер в формате E.164")
    country_iso: str = Field(..., description="ISO код страны (ISO 3166-1 alpha-2)")
    country_code: int = Field(..., description="Код страны")
    mnc: int = Field(..., description="Код мобильной сети")
    number: int = Field(..., description="Локальный номер без кода страны")
    provider: str = Field(..., description="Оператор связи")
    company: str = Field(..., description="Компания оператора (только для RU)")
    country: str = Field(..., description="Страна")
    region: str = Field(..., description="Регион (только для RU)")
    city: str = Field(..., description="Город (только для RU)")
    phone_format: str = Field(..., description="Номер в национальном формате")
    cost: float = Field(..., description="Стоимость услуги")
    balance: float = Field(..., description="Текущий баланс аккаунта")

    class Config:
        json_schema_extra = {
            "source": "+7 909 100-00-00",
            "error": "Invalid phone number",
            "mobile": 1,
            "phone": 79091000000,
            "country_iso": "RU",
            "country_code": 7,
            "mnc": 99,
            "number": 9091000000,
            "provider": "Beeline",
            "company": "ОАО \"Вымпел-Коммуникации\"",
            "country": "Россия",
            "region": "Пермский край",
            "city": "Пермь",
            "phone_format": "+7 909 100-00-00",
            "cost": 0.04,
            "balance": 50.48
        }


class HealthModel(BaseModel):
    status: bool
    database: bool
    providers: bool

    class Config:
        json_schema_extra = {
            "status": True,
            "database": True,
            "providers": True
        }
