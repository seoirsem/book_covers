import requests
from bs4 import BeautifulSoup



url = "https://www.goodreads.com/book/show/1"

page = requests.get(url)

soup = BeautifulSoup(page.content, "html.parser")

results = soup.find(id="Title")

print(results)