import requests
import crocodoc

def document(uuid, pdf=False, annotated=False, user_filter=None):
    querystring = "uuid=%s&token=%s" % (uuid, crocodoc.api_token)
    if pdf:
        querystring += "&pdf=true"
    if annotated:
        querystring += "&annotated=true"
    if filter:
        querystring += "&filter=%s" % (user_filter,)

    url = crocodoc.base_url + "download/document?" + querystring
    r = requests.get(url)
    
    crocodoc.check_response(r, True)
    
    return r.content
    
    
def thumbnail(uuid, width=None, height=None):
    querystring = "uuid=%s&token=%s" % (uuid, crocodoc.api_token)
    if width is not None and height is not None:
        querystring += "&size=%dx%d" % (width, height)

    url = crocodoc.base_url + "download/thumbnail?" + querystring
    r = requests.get(url)
    
    crocodoc.check_response(r, True)
    
    return r.content
    
    
def text(uuid):
    querystring = "uuid=%s&token=%s" % (uuid, crocodoc.api_token)
    url = crocodoc.base_url + "download/text?" + querystring
    r = requests.get(url)
    
    crocodoc.check_response(r, True)
    
    return r.content
