import requests
from pprint import pprint
import json
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('API_KEY')

def getContent(search_term, reference, date_from = ""):
    date_from = date_from.replace("date_from", "from-date")
    url = f'https://content.guardianapis.com/search?q={search_term}&{date_from}&api-key={api_key}'
    response = requests.get(url)
    articles = response.json()["response"]["results"]

    my_articles = {reference :[]}
    for index,item in enumerate(articles):
        myArticle = {'webPublicationDate' : articles[index]['webPublicationDate'],
                    'webTitle' : articles[index]['webTitle'],
                    'webUrl' : articles[index]['webUrl']
                    }
        my_articles[reference].append(myArticle)

    print(json.dumps(my_articles))


getContent("machine learning", "guardian_content", "date_from=2023-01-01")