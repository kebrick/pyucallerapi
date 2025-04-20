# pyucallerapi

## Python services for convenient work with uCaller api

### Requirements
- Python 3.5 or higher.

### Install
    pip install pyucallerapi
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
        print("Good job comrade!", call_response.get("ucaller_id"))
    else:
        # Display error message
        print(call_response.get("error", None))  

        # Display error code and Cyrillic decryption
        print(call_response.get("code"), api.check_error_code(call_response.get("code"))) 
