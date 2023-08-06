import requests
import crocodoc

def create(uuid, **kwargs):
    data = { "uuid": uuid, "token": crocodoc.api_token } 

    # validate session parameters
    boolean_parameters = ("editable", "admin", "downloadable", "copyprotected", "demo")  
    for key in kwargs.keys():
        if key in boolean_parameters:
            data[key] = "true" if bool(kwargs[key]) else "false"
            del kwargs[key]
    
    if "user" in kwargs and "id" in kwargs["user"] and "name" in kwargs["user"]:
        data["user"] = str(kwargs["user"]["id"]) + ',' + kwargs["user"]["name"]
        del kwargs["user"]
            
    if "filter" in kwargs:
        data["filter"] = kwargs["filter"]
        del kwargs["filter"]
        
    if "sidebar" in kwargs:
        data["sidebar"] = kwargs["sidebar"]
        del kwargs["sidebar"]
    
    r = requests.post(crocodoc.base_url + "session/create", data)
    
    crocodoc.check_response(r)
    
    if "session" not in r.json():
        raise crocodoc.CrocodocError("missing_session_key", r)

    return r.json()["session"]
