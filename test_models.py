import pytest
from datetime import datetime
from pyucallerapi import (
    BaseCallDataModel,
    ErrorResponseModel,
    InitCallModel,
    InitRepeatModel,
    PhoneInfo,
    GetInfoModel,
    InboundCallWaitingModel,
    UcallerWebhookModel,
    GetServiceModel,
    GetBalanceModel,
    UserLog,
    GetAccountModel,
    CheckPhoneModel
)

# Helper function to get test data from model Config
def get_test_data(model_class):
    return model_class.Config.json_schema_extra

# Base models tests
def test_base_call_data_model():
    data = get_test_data(BaseCallDataModel)
    model = BaseCallDataModel(**data)
    assert model.status is True
    assert model.ucaller_id == 103000
    assert model.phone == "7900***1010"

def test_error_response_model():
    data = get_test_data(ErrorResponseModel)
    model = ErrorResponseModel(**data)
    assert model.status is False
    assert model.error == "Error"
    assert model.code == 500

# Init models tests
def test_init_call_model():
    data = get_test_data(InitCallModel)["example"]
    model = InitCallModel(**data)
    assert model.exists is True
    assert model.unique_request_id == "f32d7ab0-2695-44ee-a20c-a34262a06b90"

def test_init_repeat_model():
    data = get_test_data(InitRepeatModel)
    model = InitRepeatModel(**data)
    assert model.free_repeated is True
    assert model.code == "1000"

# GetInfo model tests
def test_get_info_model():
    data = get_test_data(GetInfoModel)
    model = GetInfoModel(**data)
    assert model.call_status == -1
    assert model.cost == 0.3
    assert model.balance == 568.12
    assert model.phone_info[0].operator == "МТС"
    assert model.is_repeated is False  # deprecated field

def test_get_info_model_without_deprecated():
    data = {k: v for k, v in get_test_data(GetInfoModel).items()
            if not k.startswith('is_repeated')}
    model = GetInfoModel(**data)
    assert model.is_repeated is None

# Webhook model tests
def test_ucaller_webhook_model():
    data = get_test_data(UcallerWebhookModel)
    model = UcallerWebhookModel(**data)
    assert model.isMnp is True
    assert model.regionName == "Пермский край"
    assert model.operatorName == "ООО Скартел"

def test_ucaller_webhook_model_without_mnp():
    data = {**get_test_data(UcallerWebhookModel), "operatorName":None,"operatorNameMnp": None,"isMnp": False}
    model = UcallerWebhookModel(**data)
    assert model.operatorName is None
    assert model.operatorNameMnp is None

# Service models tests
def test_get_service_model():
    data = get_test_data(GetServiceModel)
    model = GetServiceModel(**data)
    assert model.name == "ВКонтакте"
    assert model.owner == "example@ucaller.ru"

def test_get_balance_model():
    data = get_test_data(GetBalanceModel)
    model = GetBalanceModel(**data)
    assert model.rub_balance == 84.6
    assert model.tariff == "uni"

# Account models tests
def test_user_log_model():
    log_data = get_test_data(GetAccountModel)["logs"][0]
    log = UserLog(**log_data)
    assert log.action == "смена пароля"
    assert isinstance(log.created_datetime, datetime)

def test_get_account_model():
    data = get_test_data(GetAccountModel)
    model = GetAccountModel(**data)
    assert model.two_auth is True
    assert len(model.logs) == 1
    assert isinstance(model.created_datetime, datetime)

# Phone check model tests
def test_check_phone_model():
    data = get_test_data(CheckPhoneModel)
    model = CheckPhoneModel(**data)
    assert model.provider == "Beeline"
    assert model.city == "Пермь"
    assert model.error == "Invalid phone number"

def test_check_phone_model_without_error():
    data = {**get_test_data(CheckPhoneModel), "error": None}
    model = CheckPhoneModel(**data)
    assert model.error is None

# Parametrized tests for validation
# @pytest.mark.parametrize("field,value,valid", [
#     ("mobile", 1, True),
#     ("mobile", 0, True),
#     ("mobile", 2, False),
#     ("country_iso", "RU", True),
#     ("country_iso", "RUS", False),
# ])
# def test_phone_model_validation(field, value, valid):
#     data = {**get_test_data(CheckPhoneModel), field: value}
#     if valid:
#         CheckPhoneModel(**data)
#     else:
#         with pytest.raises(ValueError):
#             CheckPhoneModel(**data)

# Test for InboundCallWaitingModel
def test_inbound_call_waiting_model():
    data = get_test_data(InboundCallWaitingModel)
    model = InboundCallWaitingModel(**data)
    assert model.confirmation_number == "79001000011"
    assert model.phone == "7900***1010"