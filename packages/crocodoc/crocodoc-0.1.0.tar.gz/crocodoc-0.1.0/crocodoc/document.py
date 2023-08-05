import crocodoc, requests

def upload(url=None, file=None):
    #POST request
    data = { "token": crocodoc.api_token }
    files = {}
    if file:
        files["file"] = file 
    elif url:
        data["url"] = url
    else:
        raise crocodoc.CrocodocError("invalid_url_or_file_param", r)
    r = requests.post(crocodoc.base_url + "document/upload", data=data, files=files)
    
    #Error?
    crocodoc.handleresponse(r)
    
    #Success?
    if "uuid" in r.json:
        return r.json["uuid"]
    else:
        raise crocodoc.CrocodocError("missing_uuid", r)


def status(uuids):
    #Single uuid?
    single_uuid = isinstance(uuids, basestring)
    if single_uuid:
        uuids = [uuids]
    
    #GET request
    querystring = "uuids=%s&token=%s" % (",".join(uuids), crocodoc.api_token)
    url = crocodoc.base_url + "document/status?" + querystring
    r = requests.get(url)
    
    #Error?
    crocodoc.handleresponse(r)
    
    #Success!
    return r.json[0] if single_uuid else r.json


def delete(uuid):
    #POST request
    data = { "uuid": uuid, "token": crocodoc.api_token }
    url = crocodoc.base_url + "document/delete"
    r = requests.post(url, data)
    
    #Error?
    crocodoc.handleresponse(r)

    #Success!
    return True
