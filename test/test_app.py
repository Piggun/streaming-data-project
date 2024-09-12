import requests
import unittest
from unittest.mock import patch, MagicMock
from app import (
    get_request_count,
    increment_request_count,
    can_make_request,
    get_content,
    KinesisPublisher,
    SQSPublisher,
    lambda_handler,
)

# Mock the environment variables
@patch.dict('os.environ', {'API_KEY': 'dummy_api_key', 'SQS_URL': 'dummy_sqs_url'})
class TestMyModule(unittest.TestCase):
    
    @patch('app.table.get_item')
    def test_get_request_count_success(self, mock_get_item):
        mock_get_item.return_value = {'Item': {'Count': 10}}
        
        count = get_request_count()
        
        self.assertEqual(count, 10)
    
    @patch('app.table.get_item')
    def test_get_request_count_no_item(self, mock_get_item):
        """Test that get_request_count returns 0 when no 'Item' is found"""
        mock_get_item.return_value = {}
        
        count = get_request_count()
        
        self.assertEqual(count, 0)

    @patch('app.table.update_item')
    def test_increment_request_count_success(self, mock_update_item):
        """Test that table.update_item gets called once"""
        increment_request_count()
        
        mock_update_item.assert_called_once()
    
    @patch('app.get_request_count')
    @patch('app.increment_request_count')
    def test_can_make_request_under_limit(self, mock_increment_request_count, mock_get_request_count):
        """Test that if the request count is under the limit it returns True"""
        mock_get_request_count.return_value = 40
        result = can_make_request()
        
        self.assertTrue(result)
        mock_increment_request_count.assert_called_once()
    
    @patch('app.get_request_count', return_value=50)
    def test_can_make_request_over_limit(self, mock_get_request_count):
        """Test that if the request count is over the limit it returns False"""
        mock_get_request_count.return_value = 50
        result = can_make_request()
        
        self.assertFalse(result)
    
    @patch('app.requests.get')
    def test_get_content_success(self, mock_requests_get):
        """Test that get_content returns the desired output"""
        # Mock The Guardian API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": {
                "results": [
                    {
                        "webPublicationDate": "2023-09-12",
                        "webTitle": "Test Title",
                        "webUrl": "https://test.com",
                        "fields": {"body": "This is the content of the article."},
                    }
                ]
            }
        }
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response
        
        result = get_content("test_term", "test_reference")
        
        expected_result = {
            "test_reference": [
                {
                    "webPublicationDate": "2023-09-12",
                    "webTitle": "Test Title",
                    "webUrl": "https://test.com",
                    "contentPreview": "This is the content of the article."[:1000],
                }
            ]
        }
        
        self.assertEqual(result, expected_result)
    
    @patch('app.requests.get', side_effect=requests.exceptions.RequestException)
    def test_get_content_request_exception(self, mock_requests_get):
        """Test that get_content returns an empty dictionary when raising an exception"""
        result = get_content("test_term", "test_reference")

        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()