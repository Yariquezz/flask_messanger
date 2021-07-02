import unittest
import app as tested_app
from app import wit, send_message
import json
from datetime import datetime


class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        tested_app.app.config['TESTING'] = True
        self.app = tested_app.app.test_client()

    def test_wit(self):
        message = "Some text"
        self.assertIsInstance(wit(message), str)

    def test_send_message(self):
        chat_id = 532954032
        text = 'test message'
        self.assertEqual(send_message(chat_id, text), False)

    def test_receive_update(self):
        data = {
            "update_id": 690694309,
            "message": {
                "message_id": 449,
                "from": {
                    "id": 532954034,
                    "is_bot": False,
                    "first_name": "TestFirstName",
                    "last_name": "TestLastName",
                    "username": "test_username",
                    "language_code": "uk",
                    "chat": {
                        "id": 532954034,
                        "first_name": "TestFirstName",
                        "last_name": "TestLastName",
                        "username": "test_username",
                        "type": "private"
                    },
                    "date": datetime.now().timestamp(),
                    "text": "Банк"
                }
            }
        }
        response = self.app.post(
            '/telegram/webhook',
            content_type='application/json',
            data=json.dumps(data)
        )
        self.assertEqual(response.json, {"ok": True})
        self.assertEqual(response.status_code, 200)

    def test_incoming(self):
        data = {
            'event': 'message',
            'timestamp': datetime.now().timestamp(),
            'chat_hostname': 'SN-CHAT-04_',
            'message_token': 5591655293486841164,
            'sender': {
                'id': 'H6yqdM0dAl701d61ICrQsA==',
                'name': 'Test User',
                'avatar': '',
                'language': 'uk',
                'country': 'UA',
                'api_version': 10
            },
            'message': {
                'text': 'Йоу',
                'type': 'text'
            },
            'silent': False
        }

        response = self.app.post(
            '/viber/webhook',
            content_type='application/json',
            data=json.dumps(data)
        )
        self.assertEqual(response.status_code, 403)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
