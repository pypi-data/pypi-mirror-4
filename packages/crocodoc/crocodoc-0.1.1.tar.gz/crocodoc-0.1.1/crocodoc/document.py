import requests
import crocodoc

def upload(url=None, file=None):
    data = { "token": crocodoc.api_token }
    files = {}

    if file:
        files["file"] = file 
    elif url:
        data["url"] = url
    else:
        raise crocodoc.CrocodocError("invalid_url_or_file_param")

    r = requests.post(crocodoc.base_url + "document/upload", data=data, files=files)
    
    crocodoc.check_response(r)
    
    if "uuid" not in r.json():
        raise crocodoc.CrocodocError("missing_uuid", r)

    return r.json()["uuid"]


def status(uuids):
    single_uuid = isinstance(uuids, basestring)
    if single_uuid:
        uuids = [uuids]
    
    querystring = "uuids=%s&token=%s" % (",".join(uuids), crocodoc.api_token)
    url = crocodoc.base_url + "document/status?" + querystring
    r = requests.get(url)
    
    crocodoc.check_response(r)
    
    return r.json()[0] if single_uuid else r.json()


def delete(uuid):
    data = { "uuid": uuid, "token": crocodoc.api_token }
    url = crocodoc.base_url + "document/delete"
    r = requests.post(url, data)
    
    crocodoc.check_response(r)

    return True
