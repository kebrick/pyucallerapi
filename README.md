# pyucallerapi - Python service for convenient work with uCaller API

![](https://www.python.org/static/img/python-logo.png) 

# Documentation uCaller api: [DOC](https://developer.ucaller.ru)

Установка
============

Пользуем pip:
    
```
pip install pyucallerapi
```

Зависимости
    
    python>=3.10
    requests
    pydantic>=2.9.2

    
Как использовать
============
Все названия методов соответствуют action в ссылке (смотрите документацию).
**Пример названия метода:** 

- _/v1.0/**initCall**/ - `init_сall`_

**Варианты импорта**
Вы можете импортировать

    UCallerAPI - с всеми доступными методами 
    SettingAPI - только методы для работы с аккаунтом
    CallAPI - только запросы кода авторизации

Так же прошу вас обратить **внимание** на аннотацию типов аргументов 

Если вам нужно чтобы ответ был в dict - то при инициализации укажите аргумент **return_dict** = True
    
    api = UCallerAPI(token, return_dict=True)

    # Либо
    api = TelefonIpAPI(token,)
    api.return_dict = True

# Example

### Использование сервиса 

    import logging
    from pyucallerapi import APIUCaller, CallAPI, SettingAPI
    

    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

    service_id = <int>
    key = ""
    # запрашиваем звонок 
    api = APIUCaller(
        service_id=service_id,
        key=key,
        logger=logger
    )
    # Проверка работоспособности сервиса -> HealthModel | ErrorResponseModel
    api.health()

    # Запрос на авторизацию ->  InitCallModel | ErrorResponseModel
    out = api.init_call("+79000000001", "6123",) 
    
    # получить информацию о запросе авторизации 
    api.get_info(out.ucaller_id)



    
### Получение данных webhook (например, из FastAPI)
    from fastapi import APIRouter, Request
    from pyucallerapi import UcallerWebhookModel   

    router = APIRouter()
    
    @router.post("/ucaller-webhook")
    async def handle_webhook(request: Request):
        data = await request.json()
        webhook = UcallerWebhookRequest(**data)  # Валидация
        
    if webhook.isMnp:
        print(f"Номер портирован от {webhook.operatorName} к {webhook.operatorNameMnp}")
    
    return {"status": "ok"}