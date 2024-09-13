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

    @patch('boto3.client')
    def test_kinesis_publisher_success(self, mock_boto_client):
        """Test that KinesisPublisher.publish_message works correctly"""
        mock_kinesis_client = MagicMock()
        mock_kinesis_client.put_record.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
        
        mock_boto_client.return_value = mock_kinesis_client

        publisher = KinesisPublisher("test_stream")

        response = publisher.publish_message({"message": "test"}, "test_key")
        
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
        mock_kinesis_client.put_record.assert_called_once_with(
            StreamName="test_stream",
            Data='{"message": "test"}',
            PartitionKey="test_key"
        )

    @patch('boto3.client')
    def test_kinesis_publisher_failure(self, mock_boto_client):
        """Test that KinesisPublisher.publish_message handles error correctly"""
        mock_kinesis_client = MagicMock()
        mock_kinesis_client.put_record.side_effect = Exception("Test Error")

        mock_boto_client.return_value = mock_kinesis_client

        publisher = KinesisPublisher("test_stream")

        with patch('builtins.print') as mocked_print:
            publisher.publish_message({"message": "test"}, "test_key")
            mocked_print.assert_called_with("Error publishing message to Kinesis: Test Error")

    @patch('boto3.client')
    def test_sqs_publisher_success(self, mock_boto_client):
        """Test that SQSPublisher.publish_message works correctly"""
        mock_sqs_client = MagicMock()
        mock_sqs_client.send_message.return_value = {"MessageId": "1234"}
        
        mock_boto_client.return_value = mock_sqs_client

        publisher = SQSPublisher("dummy_sqs_url")

        response = publisher.publish_message({"message": "test"}, "test_label")
        
        self.assertEqual(response["MessageId"], "1234")
        mock_sqs_client.send_message.assert_called_once_with(
            QueueUrl="dummy_sqs_url",
            MessageBody='{"message": "test"}',
            MessageAttributes={
                "ID": {"StringValue": "test_label", "DataType": "String"}
            }
        )

    @patch('boto3.client')
    def test_sqs_publisher_failure(self, mock_boto_client):
        """Test that SQSPublisher.publish_message handles error correctly"""
        mock_sqs_client = MagicMock()
        mock_sqs_client.send_message.side_effect = Exception("Test Error")

        mock_boto_client.return_value = mock_sqs_client

        publisher = SQSPublisher("dummy_sqs_url")

        with patch('builtins.print') as mocked_print:
            publisher.publish_message({"message": "test"}, "test_label")

            mocked_print.assert_called_with("Error publishing message to SQS: Test Error")

    @patch('app.can_make_request', return_value=False)
    def test_lambda_handler_request_limit_reached(self, mock_can_make_request):
        """Test that can_make_request works correctly"""
        event = {
            "search_term": "test_term",
            "reference": "test_reference",
            "date_from": "2023-09-12"
        }
        
        with patch('builtins.print') as mocked_print:
            lambda_handler(event, "context")
            mocked_print.assert_called_with("Limit of 50 requests per day reached, try again tomorrow.")

if __name__ == '__main__':
    unittest.main()