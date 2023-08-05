import crocodoc, requests

def document(uuid, pdf=False, annotated=False, filter=None):
    #Build query string
    querystring = "uuid=%s&token=%s" % (uuid, crocodoc.api_token)
    if pdf:
        querystring += "&pdf=true"
    if annotated:
        querystring += "&annotated=true"
    if filter:
        querystring += "&filter=%s" % (filter,)

    #GET request
    url = crocodoc.base_url + "download/document?" + querystring
    r = requests.get(url)
    
    #Error?
    crocodoc.handleresponse(r, True)
    
    #Success!
    return r.content
    
    
def thumbnail(uuid, width=None, height=None):
    #Build query string
    querystring = "uuid=%s&token=%s" % (uuid, crocodoc.api_token)
    
    if width is not None and height is not None:
        querystring += "&size=%dx%d" % (width, height)

    #GET request
    url = crocodoc.base_url + "download/thumbnail?" + querystring
    r = requests.get(url)
    
    #Error?
    crocodoc.handleresponse(r, True)
    
    #Success!
    return r.content
    
    
def text(uuid):
    #GET request
    querystring = "uuid=%s&token=%s" % (uuid, crocodoc.api_token)
    url = crocodoc.base_url + "download/text?" + querystring
    r = requests.get(url)
    
    #Error?
    crocodoc.handleresponse(r, True)
    
    #Success!
    return r.content
