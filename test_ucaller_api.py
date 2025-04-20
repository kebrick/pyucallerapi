import pytest
from unittest.mock import Mock, patch

import requests
from requests import Session, Response
from datetime import datetime
import json
import logging

from pyucallerapi import (
    SettingAPI,
    CallAPI,
    APIUCaller,
    InitCallModel,
    InitRepeatModel,
    GetInfoModel,
    InboundCallWaitingModel,
    GetServiceModel,
    GetBalanceModel,
    GetAccountModel,
    CheckPhoneModel,
    ErrorResponseModel,
)


# Fixtures
@pytest.fixture
def mock_session():
    return Mock(spec=Session)


@pytest.fixture
def api(mock_session):
    return APIUCaller(service_id=123, key="32_characters_long_test_key_1234", session=mock_session)


def create_mock_response(status_code=200, json_data=None, text=None):
    response = Mock(spec=Response)
    response.status_code = status_code

    if json_data:
        response.json.return_value = json_data
        response.text = json.dumps(json_data)
        response.content = json.dumps(json_data).encode('utf-8')
    elif text:
        response.text = text
        response.content = text.encode('utf-8')

    return response

# BaseAPI tests
def test_base_api_initialization(api):
    assert api.service_id== 123
    assert api.key == "32_characters_long_test_key_1234"
    assert isinstance(api.session_s, Mock)


def test_validate_phone_number(api):
    valid_phones = [
        ("89091234567", "+79091234567"),
        ("79091234567", "+79091234567"),
        ("8(909)123-45-67", "+79091234567"),
        ("7 909 123 45 67", "+79091234567")
    ]

    for phone, expected in valid_phones:
        assert api._validate_phone_number(phone, country_code_format="+7", re_sub_repl=r'\1\2\3\4') == expected


def test_validate_phone_number_invalid(api):
    invalid_phones = ["12345", "890912345", "790912345678", "abc"]
    for phone in invalid_phones:
        with pytest.raises(ValueError):
            api._validate_phone_number(phone)


def test_validate_code(api):
    assert api._validate_code("1234") == "1234"
    assert api._validate_code("12-34") == "1234"
    with pytest.raises(AssertionError):
        api._validate_code("123")
    with pytest.raises(AssertionError):
        api._validate_code(1234)  # Not a string


# SettingAPI tests
def test_get_service_success(api, mock_session):
    test_data = {
        "status": True,
        "service_status": 1,
        "name": "Test Service",
        "creation_time": 1234567890,
        "last_request": 1234567890,
        "owner": "test@example.com",
        "use_direction": "Test"
    }
    mock_response = create_mock_response(json_data=test_data)
    mock_session.get.return_value = mock_response

    result = api.get_service()
    assert isinstance(result, GetServiceModel)
    assert result.name == "Test Service"


def test_get_service_error(api, mock_session):
    test_data = {
        "status": False,
        "error": "Service not found",
        "code": 404
    }
    mock_response = create_mock_response(json_data=test_data)
    mock_session.get.return_value = mock_response

    result = api.get_service()
    assert isinstance(result, ErrorResponseModel)
    assert result.error == "Service not found"


def test_get_balance_success(api, mock_session):
    test_data = {
        "status": True,
        "rub_balance": 100.5,
        "tariff": "test",
        "tariff_name": "Test Tariff"
    }
    mock_response = create_mock_response(json_data=test_data)
    mock_session.get.return_value = mock_response

    result = api.get_balance()
    assert isinstance(result, GetBalanceModel)
    assert result.rub_balance == 100.5


# CallAPI tests
def test_init_call_success(api, mock_session):
    test_data = {
        "status": True,
        "ucaller_id": 12345,
        "phone": "79001234567",
        "code": "1234",
        "exists": True
    }
    mock_response = create_mock_response(json_data=test_data)
    mock_session.get.return_value = mock_response

    result = api.init_call(phone="89091234567", code="1234")
    assert isinstance(result, InitCallModel)
    assert result.ucaller_id == 12345
    assert result.exists is True


def test_init_call_with_client_and_unique(api, mock_session):
    test_data = {
        "status": True,
        "ucaller_id": 12345,
        "phone": "79001234567",
        "code": "1234",
        "exists": True,
        "client": "test_client",
        "unique_request_id": "test_unique"
    }
    mock_response = create_mock_response(json_data=test_data)
    mock_session.get.return_value = mock_response

    result = api.init_call(
        phone="89091234567",
        code="1234",
        client="test_client_64_characters_long_string_12345678901234567890fe8712",
        unique="test_unique_64_characters_long_string_12345678901234567890fe8712"
    )
    assert result.client == "test_client"



def test_get_info_success(api, mock_session):
    test_data = {
        "status": True,
        "ucaller_id": 12345,
        "phone": "79001234567",
        "init_time": 1234567890,
        "call_status": 1,
        "country_code": "RU",
        "cost": 0.5,
        "balance": 100.0
    }
    mock_response = create_mock_response(json_data=test_data)
    mock_session.get.return_value = mock_response

    result = api.get_info(uid="12345")
    assert isinstance(result, GetInfoModel)
    assert result.call_status == 1
    assert result.country_code == "RU"


def test_inbound_call_waiting_success(api, mock_session):
    test_data = {
        "status": True,
        "ucaller_id": 12345,
        "phone": "79001234567",
        "confirmation_number": "79001234567"
    }
    mock_response = create_mock_response(json_data=test_data)
    mock_session.get.return_value = mock_response

    result = api.inbound_call_waiting(
        phone="89091234567",
        callback_url="https://example.com/callback"
    )
    assert isinstance(result, InboundCallWaitingModel)
    assert result.confirmation_number == "79001234567"


def test_check_phone_success(api, mock_session):
    test_data = {
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
    mock_response = create_mock_response(json_data=test_data)
    mock_session.get.return_value = mock_response

    result = api.check_phone(phone="89091000000")
    assert isinstance(result, CheckPhoneModel)
    assert result.provider == "Beeline"
    assert result.city == "Пермь"


# Error handling tests
def test_api_request_exception(api, mock_session, caplog):
    mock_session.get.side_effect = ConnectionError("Connection error")

    with caplog.at_level(logging.ERROR):
        result = api.init_call(phone="89091234567", code="1234")

    assert "Ошибка подключения" in caplog.text
    assert result is None


def test_invalid_key_initialization():
    with pytest.raises(AssertionError):
        APIUCaller(service_id=123, key="too_short")


# Test return_dict option
def test_return_dict_option(mock_session):
    api = APIUCaller(
        service_id=123,
        key="32_characters_long_test_key_1234",
        session=mock_session,
        return_dict=True
    )

    test_data = {"status": True, "test": "value"}
    mock_response = create_mock_response(json_data=test_data)
    mock_session.get.return_value = mock_response

    result = api.get_service()
    assert isinstance(result, dict)
    assert result["test"] == "value"


# Test deprecated method
def test_deprecated_method(api, mock_session, recwarn):
    test_data = {
            "status": True,
            "ucaller_id": 103000,
            "phone": "7900***1010",
            "code": "1000",
            "client": "nickname",
            "unique_request_id": "f32d7ab0-2695-44ee-a20c-a34262a06b90",
            "exists": True,
            "free_repeated": True

        }
    mock_response = create_mock_response(json_data=test_data)
    mock_session.get.return_value = mock_response

    # with caplog.at_level(logging.WARN):
    result = api.init_repeat(uid="12345")

    # Проверяем, что было вызвано предупреждение
    assert len(recwarn) == 1
    warning = recwarn.pop(DeprecationWarning)
    assert "Метод больше не поддерживается" in str(warning.message)
    assert result is not None