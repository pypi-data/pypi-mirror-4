import urllib
import requests

from parsers import JSONParser


class ApiException(Exception):
    pass


class NoArgsException(ApiException):
    pass


class TooMuchArgsException(ApiException):
    pass


class HttpError(ApiException):
    pass


class Api(object):

    def __init__(self, parser=None, url=None):

        self.api_url = url or 'http://api.peerreach.com/v1'
        self.api_user_url = self.api_url + '/user/lookup.json'
        self.api_multi_user_url = self.api_url + '/multi-user/lookup.json'

        if parser:
            self.parser = parser
        else:
            self.parser = JSONParser()

    def parse(self, data):
        return self.parser.parse(data)

    def get_data(self, url, **options):

        response = requests.get(url, **options)

        if str(response.status_code)[0] != '2':
            raise HttpError(response.status_code)

        return self.parse(response.text)

    def user_lookup(self, user_id=None, screen_name=None):
        if not any((user_id, screen_name)):
            raise NoArgsException()
        if all((user_id, screen_name)):
            raise TooMuchArgsException()

        if user_id:
            params = {"user_id": user_id}
        else:
            params = {"screen_name": screen_name}

        url = "%s?%s" % (self.api_user_url, urllib.urlencode(params))

        return self.get_data(url)

    def multi_user_lookup(self, user_ids=None, screen_names=None):
        if not any((user_ids, screen_names)):
            raise NoArgsException()
        if all((user_ids, screen_names)):
            raise TooMuchArgsException()

        if user_ids:
            params = {"user_id": ",".join(map(str, user_ids))}
        else:
            params = {"screen_name": ",".join(screen_names)}

        url = "%s?%s" % (self.api_multi_user_url, urllib.urlencode(params))

        return self.get_data(url)
