from crocodoc import document
from crocodoc import session
from crocodoc import download


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
        return "\n\t%s \n\tResponse status code: %s \n\tResponse content: %s" % (self.error_message, self.status_code, content)


def check_response(r, ignore_json=False):
    if not ignore_json:
        if not r.json():
            raise CrocodocError("server_response_not_valid_json", r)
        elif isinstance(r.json(), dict) and "error" in r.json():
            raise CrocodocError(r.json()["error"], r)

    http_4xx_error_codes = {
        400: 'bad_request',
        401: 'unauthorized',
        404: 'not_found',
        405: 'method_not_allowed'
    }
    
    if r.status_code in http_4xx_error_codes:
        error = 'server_error_%s_%s' % (r.status_code, http_4xx_error_codes[r.status_code])
        raise CrocodocError(error, r)
    elif r.status_code >= 500 and r.status_code < 600:
        error = 'server_error_%s_unknown' % (r.status_code,)
        raise CrocodocError(error, r)
