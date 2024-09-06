import requests
from pprint import pprint
import boto3
import json
from dotenv import load_dotenv
import os
import argparse

load_dotenv()

api_key = os.getenv('API_KEY')


def get_content(search_term:str, reference:str, date_from = "") -> dict:
    """
    Retrievs articles from The Guadian API.

    Returns: A `dictionary` with the `reference` as the first `key` and a `list` of articles as its `pair`.

    :param search_term: A `string` used to determine the type of articles you want to search for.
    :param reference: A `string` used to set a reference to use for the message.
    :param date_from: A `string` used to set the starting date from which to look for articles.
    """
    date_from = date_from.replace("date_from", "from-date")
    url = f'https://content.guardianapis.com/search?q={search_term}&{date_from}&api-key={api_key}'
    params = {
        'show-fields': 'body'  # Include the article body in the response
    }
    response = requests.get(url, params=params)
    articles = response.json()["response"]["results"]

    my_articles = {reference :[]}
    for index,item in enumerate(articles):
        my_article = {'webPublicationDate' : articles[index]['webPublicationDate'],
                    'webTitle' : articles[index]['webTitle'],
                    'webUrl' : articles[index]['webUrl'],
                    'contentPreview' : articles[index]['fields']['body'][:1000]  # limit to first 1000 characters
                    }
        my_articles[reference].append(my_article)
    return my_articles

# Using AWS Kines as an alternative to AWS SQS
class KinesisPublisher:
    def __init__(self, stream_name, region_name='eu-west-2'):
        self.stream_name = stream_name
        self.client = boto3.client('kinesis', region_name=region_name)

    def publish_message(self, data, partition_key):
        """
        Publishes a message to the Kinesis stream.
        
        :param data: A `dictionary` containing the data to send.
        :param partition_key: A `string` used to determine the shard to which the data record is assigned.
        """
        response = self.client.put_record(
            StreamName=self.stream_name,
            Data=json.dumps(data),
            PartitionKey=partition_key
        )
        return response


class SQSPublisher:
    def __init__(self, queue_url, region_name='eu-west-2'):
        self.queue_url = queue_url
        self.client = boto3.client('sqs', region_name=region_name)

    def publish_message(self, data, label):
        """
        Publishes a message to the SQS queue.
        
        :param data: A dictionary containing the data to send.
        """
        response = self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(data),
            MessageAttributes={
            'ID': {
                'StringValue': label,
                'DataType': 'String'
                }
            }
        )
        return response


def lambda_handler(event, context):
    # kinesis_publisher = KinesisPublisher('the_guardian_articles')
    # message = get_content("tennis", "guardian_tennis_content", "date_from=2023-01-01")

    # reference = list(message)[0]
    # for article in message[reference]:
    #     response = kinesis_publisher.publish_message(data=article, partition_key=reference)
    #     print(response)

    if 'date_from' not in event:    # Prevents app from crashing when no 'date_from' key is passed in the event
        event['date_from'] = ""

    sqs_publisher = SQSPublisher('https://sqs.eu-west-2.amazonaws.com/195275642800/the_guardian_articles')
    message = get_content(event['search_term'], event['reference'], event['date_from'])
    reference = list(message)[0]

    for article in message[reference]:
        response = sqs_publisher.publish_message(data=article, label=reference)
        print(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetches articles from the Guardian API and publish them to AWS SQS.")
    
    # Add arguments for search_term, date_from, and stream_name
    parser.add_argument("--search_term", type=str, required=True, help="The search term for the Guardian API.")
    parser.add_argument("--reference", type=str, required=True,  help="The reference label of the SQS message.")
    parser.add_argument("--date_from", type=str, required=False, default="", help="The starting date for searching articles (format: date_from=YYYY-MM-DD).")

    # Parse the arguments from the command line
    args = parser.parse_args()

    search_term = args.search_term
    reference = args.reference
    date_from = args.date_from

    lambda_handler({"search_term": search_term, "reference": reference, "date_from" : date_from},"context")