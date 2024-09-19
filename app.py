import requests
import boto3
import json
from dotenv import load_dotenv
from datetime import datetime
from botocore.exceptions import ClientError
import os
import argparse

load_dotenv()

API_KEY = os.getenv("API_KEY")
SQS_URL = os.getenv("SQS_URL")
REQUEST_LIMIT = 50

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("request-counter")


def get_request_count():
    try:
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        # Try to get the count for today from DynamoDB
        response = table.get_item(Key={"Date": today})
        return response.get("Item", {}).get("Count", 0)
    except ClientError as e:
        print(f"Error fetching request count from DynamoDB: {e}")
        return 0


def increment_request_count():
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        # Increment the counter for today
        table.update_item(
            Key={"Date": today},
            UpdateExpression="ADD #count :inc",
            ExpressionAttributeNames={"#count": "Count"},
            ExpressionAttributeValues={":inc": 1},
            ReturnValues="UPDATED_NEW",
        )
    except ClientError as e:
        print(f"Error incrementing request count in DynamoDB: {e}")


def can_make_request():
    try:
        request_count = get_request_count()

        if request_count < REQUEST_LIMIT:
            increment_request_count()
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking request limit: {e}")
        return False


def get_content(search_term: str, reference: str, date_from="") -> dict:
    """
    Retrievs articles from The Guadian API.

    Returns: A `dictionary` with the `reference` as the first `key`
    and a `list` of articles as its `value`.

    :param search_term: A `string` used to determine the type of
    articles you want to search for.
    :param reference: A `string` used to set a reference to use
     for the message.
    :param date_from: A `string` used to set the starting date from
     which to look for articles.
    """
    try:
        url = (
            f"https://content.guardianapis.com/search?q="
            f"{search_term}&api-key={API_KEY}"
        )
        if date_from != "":
            url += f"&from-date={date_from}"
        params = {
            "show-fields": "body",  # Include the article body in the response
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200:
            raise Exception(
                f"Error: Received status code {response.status_code}"
                " from Guardian API"
            )

        if "response" not in response.json():
            raise KeyError("'response' key not found in the API response")

        articles = response.json()["response"]["results"]

        my_articles = {reference: []}
        for index, item in enumerate(articles):
            my_article = {
                "webPublicationDate": articles[index]["webPublicationDate"],
                "webTitle": articles[index]["webTitle"],
                "webUrl": articles[index]["webUrl"],
                "contentPreview": articles[index]["fields"]["body"][
                    :1000
                ],  # limit to first 1000 characters
            }
            my_articles[reference].append(my_article)
        return my_articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from The Guardian API: {e}")
        return {}
    except KeyError as e:
        print(f"Error processing article data: Missing key {e}")
        return {}


# Using AWS Kines as an alternative to AWS SQS
class KinesisPublisher:
    def __init__(self, stream_name, region_name="eu-west-2"):
        self.stream_name = stream_name
        self.client = boto3.client("kinesis", region_name=region_name)

    def publish_message(self, data, partition_key):
        """
        Publishes a message to the Kinesis stream.

        :param data: A `dictionary` containing the data to send.
        :param partition_key: A `string` used to determine the shard
         to which the data record is assigned.
        """
        try:
            response = self.client.put_record(
                StreamName=self.stream_name,
                Data=json.dumps(data),
                PartitionKey=partition_key,
            )
            return response
        except Exception as e:
            print(f"Error publishing message to Kinesis: {e}")


class SQSPublisher:
    def __init__(self, queue_url, region_name="eu-west-2"):
        self.queue_url = queue_url
        self.client = boto3.client("sqs", region_name=region_name)

    def publish_message(self, data, label):
        """
        Publishes a message to the SQS queue.

        :param data: A dictionary containing the data to send.
        """
        try:
            response = self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(data),
                MessageAttributes={
                    "ID": {"StringValue": label, "DataType": "String"}
                },
            )
            return response
        except Exception as e:
            print(f"Error publishing message to SQS: {e}")
            raise e


def lambda_handler(event, context):
    try:
        if can_make_request():
            # Prevents app from crashing when no 'date_from'
            # key is passed in the event
            if "date_from" not in event:
                event["date_from"] = ""

            sqs_publisher = SQSPublisher(SQS_URL)
            message = get_content(
                event["search_term"], event["reference"], event["date_from"]
            )
            reference = list(message)[0]

            for article in message[reference]:
                sqs_publisher.publish_message(data=article, label=reference)
            print("The retrieved articles have been published to AWS SQS!")
        else:
            print(
                f"Limit of {REQUEST_LIMIT} requests per day reached, "
                "try again tomorrow."
            )
    except Exception as e:
        print(f"Error in lambda_handler: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetches articles from the Guardian API and"
        " publish them to AWS SQS."
    )

    # Add arguments for search_term, date_from, and stream_name
    parser.add_argument(
        "--search_term",
        type=str,
        required=True,
        help="The search term for the Guardian API.",
    )
    parser.add_argument(
        "--reference",
        type=str,
        required=True,
        help="The reference label of the SQS message.",
    )
    parser.add_argument(
        "--date_from",
        type=str,
        required=False,
        default="",
        help="The starting date for searching articles"
        " (format: YYYY-MM-DD).",
    )

    # Parse the arguments from the command line
    args = parser.parse_args()

    SEARCH_TERM = args.search_term
    REFERENCE = args.reference
    DATE_FROM = args.date_from

    lambda_handler(
        {
            "search_term": SEARCH_TERM,
            "reference": REFERENCE,
            "date_from": DATE_FROM,
        },
        "context",
    )
