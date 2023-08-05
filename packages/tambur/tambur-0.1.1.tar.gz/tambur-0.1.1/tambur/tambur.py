import hmac
import hashlib
import requests
from requests.auth import OAuth1
from oauthlib.oauth1.rfc5849 import SIGNATURE_TYPE_BODY

api_version = '1.0'

class Tambur(object):
    def __init__(self, api_key=None, app_id=None, secret=None, api_host='api.tambur.io'):
        self.api_key = str(api_key)
        self.app_id = str(app_id)
        self.secret = str(secret)
        self.api_host = str(api_host)
        self.oauth = OAuth1(unicode(self.api_key), client_secret=unicode(self.secret), signature_type=SIGNATURE_TYPE_BODY)
        self.url = 'http://'+self.api_host+'/app/'+self.app_id

    def publish(self, stream, message):
        params = {
            'api_version' : api_version,
            'message' : message
        }

        r = requests.post(self.url + '/stream/'+str(stream), data=params, auth=self.oauth)
        r.raise_for_status()
        return True

    def generate_auth_token(self, stream, subscriber_id):
        return self.__generate_mode_token('auth', stream, subscriber_id)

    def generate_presence_token(self, stream, user_id, subscriber_id):
        return self.__generate_mode_token('presence', stream + ':' + user_id, subscriber_id)

    def generate_direct_token(self, stream, user_id, subscriber_id):
        return self.__generate_mode_token('direct', stream + ':' + user_id, subscriber_id)

    def __generate_mode_token(self, mode, props, subscriber_id):
        mode_string = self.api_key + ':' + self.app_id + ':' + mode + ':' + props + ':' + subscriber_id
        return hmac.new(self.secret, mode_string, hashlib.sha1).hexdigest()
