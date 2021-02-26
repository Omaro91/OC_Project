import requests
from bs4 import BeautifulSoup

links = []
for i in range(1, 5):
    print("Page num°:", i)

    url = "http://books.toscrape.com/catalogue/category/books/fiction_10/page-"+str(i)+".html"

    response = requests.get(url)  # code 200
    response.encoding = 'UTF-8'  # a réglé les problèmes d'exportation csv
    soup = BeautifulSoup(response.text, "lxml")  # affiche la page html

    for lien in soup.find_all("h3"):
        liens = lien.a["href"]
        print(liens.replace("../../../", "http://books.toscrape.com/catalogue/"))
        links.append(liens.replace("../../../", "http://books.toscrape.com/catalogue/"))

with open("livre_category.csv", 'w') as file:
    for link in links:
        file.write(link + "\n")
