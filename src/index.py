import requests
from pprint import pprint
import json
from dotenv import load_dotenv
import os

load_dotenv()

apiKey = os.getenv('API_KEY')

def getContent(searchTerm, reference, dateFrom = ""):
    dateFrom = dateFrom.replace("date_from", "from-date")
    url = f'https://content.guardianapis.com/search?q={searchTerm}&{dateFrom}&api-key={apiKey}'
    response = requests.get(url)
    articles = response.json()["response"]["results"]

    myArticles = {reference :[]}
    for index,item in enumerate(articles):
        myArticle = {'webPublicationDate' : articles[index]['webPublicationDate'],
                    'webTitle' : articles[index]['webTitle'],
                    'webUrl' : articles[index]['webUrl']
                    }
        myArticles[reference].append(myArticle)

    print(json.dumps(myArticles))


getContent("machine learning", "guardian_content", "date_from=2023-01-01")