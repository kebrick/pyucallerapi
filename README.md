# pyucallerapi

## Python services for convenient work with uCaller api

### Requirements
- Python 3.5 or higher.

### Install
    pip install pyiikoapi
## Documentation uCaller api: [DOC](https://ucaller.ru/doc)
### Example
    from pyucallerapi import APIUCaller

    # class initialization
    api = APIUCaller(
        service_id=25742,
        key="" # string == 32 characters
    )
    
    # receive a list of the organization's couriers
    call_response = api.init_call(
        phone="9999999999",
        code="6123"
    )

    if call_response.get("status", False):
        print("Good job comrade!")	



