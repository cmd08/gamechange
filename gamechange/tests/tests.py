from flask.ext.testing import TestCase
import unittest
import gamechange

class TestBlogSite(TestCase):

    def create_app(self):
        gamechange.app.config['TESTING'] = True
        return gamechange.app

    def test_error_404(self):
        response = self.client.get("/error/404/")
        self.assert404(response)

    def test_error_403(self):
        response = self.client.get("/error/403/")
        self.assert403(response)

    def test_api(self):
        response = self.client.get("/bananas/api/")
        assert '_csrf_token' in response.json
        assert 'hostname' in response.json
        assert type(response.json['system_time_millis']) == int
        self.assertEquals(response.json['testing'], True)
        self.assertEquals(response.json['api_version'], 0.1)

if __name__ == '__main__':
    unittest.main()