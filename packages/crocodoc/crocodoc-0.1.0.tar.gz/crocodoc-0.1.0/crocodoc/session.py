import crocodoc, requests

def create(uuid, **kwargs):
    #Validate session parameters
    data = { "uuid": uuid, "token": crocodoc.api_token } 
    boolean_parameters = ("editable", "admin", "downloadable", "copyprotected", "demo")  
    for key in list(kwargs.iterkeys()):
        if key in boolean_parameters:
            data[key] = "true" if bool(kwargs[key]) else "false"
            del kwargs[key]
    
    #User?
    if "user" in kwargs and "id" in kwargs["user"] and "name" in kwargs["user"]:
        data["user"] = str(kwargs["user"]["id"]) + ',' + kwargs["user"]["name"]
        del kwargs["user"]
            
    #Filter?
    if "filter" in kwargs:
        data["filter"] = kwargs["filter"]
        del kwargs["filter"]
        
    #Sidebar?
    if "sidebar" in kwargs:
        data["sidebar"] = kwargs["sidebar"]
        del kwargs["sidebar"]
    
    #POST request
    r = requests.post(crocodoc.base_url + "session/create", data)
    
    #Error?
    crocodoc.handleresponse(r)
    
    #Success?
    if "session" in r.json:
        return r.json["session"]
    else:
        raise crocodoc.CrocodocError("missing_session_key", r)
