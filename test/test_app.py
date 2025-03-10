import unittest

from src.app import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def test_ping(self):
        response = self.client.get('/ping')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
