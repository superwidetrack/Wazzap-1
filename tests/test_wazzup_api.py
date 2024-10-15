import unittest
from api_wazzup import WazzupAPI

class TestWazzupAPI(unittest.TestCase):
    def setUp(self):
        self.api = WazzupAPI('test_key')

    def test_send_message(self):
        # Тест отправки сообщения
        pass

    def test_receive_message(self):
        # Тест получения сообщения
        pass
