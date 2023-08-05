import pywunder
import os
import unittest

from mock import patch, Mock

class ClientTestCase(unittest.TestCase):


    def load_fixture(self, filename):
        return open(os.path.join(os.path.dirname(__file__),"fixtures",  filename)).read()

    def create_mock_response(self, fixture_name, status=200, headers={}):
        content = self.load_fixture(fixture_name)
        mock_response = Mock()
        mock_response.content=content
        mock_response.status_code = status
        return mock_response

    @patch('requests.get')
    def test_forecast(self, mock_get):
        mock_get.return_value = self.create_mock_response("forecast.json")
        client = pywunder.Client("notausefulkey")
        result = client.forecast("ignored")
        self.assertEqual(len(result), 4)

    @patch('requests.get')
    def test_ambiguous_location(self, mock_get):
        mock_get.return_value = self.create_mock_response("ambig_location.json")
        client = pywunder.Client("notakey")
        with self.assertRaises(pywunder.AmbiguousLocationError):
            result = client.forecast("ignored")


