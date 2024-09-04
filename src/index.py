import requests
from pprint import pprint
import boto3
import json
from dotenv import load_dotenv
import os

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
    response = requests.get(url)
    articles = response.json()["response"]["results"]

    my_articles = {reference :[]}
    for index,item in enumerate(articles):
        my_article = {'webPublicationDate' : articles[index]['webPublicationDate'],
                    'webTitle' : articles[index]['webTitle'],
                    'webUrl' : articles[index]['webUrl']
                    }
        my_articles[reference].append(my_article)

    return my_articles


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


if __name__ == "__main__":
    kinesis_publisher = KinesisPublisher('the_guardian_articles')
    message = get_content("home", "guardian_home_content", "date_from=2023-01-01")

    reference = list(message)[0]
    for article in message[reference]:
        response = kinesis_publisher.publish_message(data=article, partition_key=reference)
        print(response)
        
