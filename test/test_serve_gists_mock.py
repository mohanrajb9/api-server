""" Unit tests for GistController with mocked web_api_helper """

import unittest
from unittest.mock import patch, MagicMock
import io
from http import HTTPStatus
import requests
from gists_controller import GistController


SERVER_ERROR = HTTPStatus.INTERNAL_SERVER_ERROR


class TestServeGistsCoverageMock(unittest.TestCase):
    """ Tests for GistController with mocked web_api_helper """
    def setupHandler(self, path):
        """ Helper to setup GistController handler """
        handler = GistController
        handler.path = path
        handler.wfile = io.BytesIO()
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        return handler

    @patch('web_api_helper.requests.get')
    def test_invalid_json(self, mock_request):
        """ Simulate invalid JSON response from GitHub API """
        mock_request.side_effect = ValueError("Invalid JSON")

        # Setup and run the handler
        handler = self.setupHandler('/gituser')
        handler.do_GET(handler)

        # Assertions
        handler.send_response.assert_called_with(SERVER_ERROR)
        output = handler.wfile.getvalue()
        self.assertIn(b'Invalid JSON response', output)

    @patch('web_api_helper.requests.get')
    def test_request_network_error(self, mock_request):
        """ Simulate network error during API request """
        raise_exception = requests.exceptions.RequestException("Network error")
        mock_request.side_effect = raise_exception

        # Setup and run the handler
        handler = self.setupHandler('/gituser')
        handler.do_GET(handler)

        handler.send_response.assert_called_with(SERVER_ERROR)
        self.assertIn(b'Network error', handler.wfile.getvalue())

    @patch('web_api_helper.requests.get')
    def test_http_error_response(self, mock_request):
        """" Simulate HTTP error (non-404) from GitHub API """
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.status_code = SERVER_ERROR
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_request.return_value = mock_response

        # Setup and run the handler
        handler = self.setupHandler('/gituser')
        handler.do_GET(handler)
        handler.send_response.assert_called_with(SERVER_ERROR)
        self.assertIn(b'HTTP error', handler.wfile.getvalue())

    def test_invalid_page_number(self):
        """ Test invalid page number parameter """
        # Setup and run the handler
        handler = self.setupHandler('/gituser?page=-1')
        handler.do_GET(handler)

        # Assertions
        handler.send_response.assert_called_with(HTTPStatus.BAD_REQUEST)
        self.assertIn(b'Usage - 127.0.0.1', handler.wfile.getvalue())
