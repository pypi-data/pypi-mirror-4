import document, session, download

api_token = ""
base_url = "https://crocodoc.com/api/v2/"

class CrocodocError(Exception):
    def __init__(self, message, response=None):
        Exception.__init__(self, message)
        self.error_message = message
        self.response_content = None
        self.status_code = None

        if response is not None:
            self.status_code = response.status_code
            self.response_content = response.content
            
    def __str__(self):
        content = self.response_content
        if self.response_content and len(self.response_content) > 100:
            content = self.response_content[:100] + "..."
        params = (self.error_message, self.status_code, content)
        return "\n\t%s \n\tResponse status code: %s \n\tResponse content: %s" % params


def handleresponse(r, ignorejson=False):
    #Check for JSON error
    if not ignorejson:
        if not r.json:
            raise CrocodocError("server_response_not_valid_json", r)
        elif isinstance(r.json, dict) and "error" in r.json:
            raise CrocodocError(r.json["error"], r)

    #Check for HTTP error
    http_4xx_error_codes = {
        400: 'bad_request',
        401: 'unauthorized',
        404: 'not_found',
        405: 'method_not_allowed'
    }
    
    if (http_4xx_error_codes.has_key(r.status_code)):
        error = 'server_error_' + r.status_code + '_' + http_4xx_error_codes[r.status_code]
        raise CrocodocError(error, r)
    elif r.status_code >= 500 and r.status_code < 600:
        error = 'server_error_' + r.status_code + '_unknown'
        raise CrocodocError(error, r)

    # if we made it this far, we're good to go