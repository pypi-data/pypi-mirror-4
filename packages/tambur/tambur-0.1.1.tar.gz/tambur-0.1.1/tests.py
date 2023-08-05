import unittest
import requests
import random
import json
from tambur import Tambur

class TamburPublishTest(unittest.TestCase):
    def setUp(self):
        self.s = requests.session()
        r = self.s.get('http://wsbot.tambur.io/credentials')
        credentials = json.loads(r.text)
        api_key = credentials['api_key']
        app_id = credentials['app_id'].encode('ascii')
        secret = credentials['secret'].encode('ascii')
        r = self.s.get('http://wsbot.tambur.io/subscriber_id')
        self.subscriber_id = r.text
        self.tambur = Tambur(api_key=api_key, app_id=app_id, secret=secret)

    def test_publish(self):
        self.__publish('test', 'test message')

    def test_auth_publish(self):
        self.__publish('auth:test', 'test message')

    def test_private_publish(self):
        self.__publish('private:'+self.subscriber_id, 'test message')

    def __publish(self, stream, msg):
        handle = generate_handle()
        msg = {'handle' : handle, 'msg' : msg}
        json_msg = json.dumps(msg)
        self.assertTrue(self.tambur.publish(stream, json_msg))
        r = self.s.get('http://wsbot.tambur.io/results?handle='+handle)
        results = json.loads(r.text)
        self.assertEqual(len(results), 1)
        if stream.startswith('private'):
            self.assertEqual(results[0][handle], {'private' : msg})
        else:
            self.assertEqual(results[0][handle], {stream : msg})

class TamburModeTokenTest(unittest.TestCase):
    def setUp(self):
        self.tambur = Tambur(api_key='30af96de47e3c58329045ff136a4a3ea', app_id='ws-bot-1', secret='wsbot')

    def test_generate_auth_token(self):
        stream = 'test'
        subscriber_id = 'a0629978-28d8-4fd4-b862-f67e9b6dfd8f'
        token = self.tambur.generate_auth_token(stream, subscriber_id)
        self.assertEqual(token, '2f25ad1ce5afab906cc582b6254a912590c60f73')

    def test_generate_presence_token(self):
        stream = 'test'
        user = 'test_user'
        subscriber_id = 'a0629978-28d8-4fd4-b862-f67e9b6dfd8f'
        token = self.tambur.generate_presence_token(stream, user, subscriber_id)
        self.assertEqual(token, 'dcadf9659116ebbe024a4cd5ae12bde48d95408e')

    def test_generate_direct_token(self):
        stream = 'test'
        user = 'test_user'
        subscriber_id = 'a0629978-28d8-4fd4-b862-f67e9b6dfd8f'
        token = self.tambur.generate_direct_token(stream, user, subscriber_id)
        self.assertEqual(token, '2403374744295f5d22e3f999d4eb85b3f689c6b2')

def generate_handle():
    return ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for x in range(6))

if __name__ == '__main__':
    unittest.main()

