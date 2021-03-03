import requests
from bs4 import BeautifulSoup


links = []

i = 1
url = "http://books.toscrape.com/catalogue/category/books/fiction_10/page-"+str(i)+".html"

while str(requests.get(url)) == "<Response [200]>":

    print("Page num°:", i)
    response = requests.get(url)  # code 200
    response.encoding = 'UTF-8'  # a réglé les problèmes d'exportation csv
    soup = BeautifulSoup(response.text, "lxml")  # affiche la page html

    for lien in soup.find_all("h3"):
        liens = lien.a["href"]
        print(liens.replace("../../../", "http://books.toscrape.com/catalogue/"))
        links.append(liens.replace("../../../", "http://books.toscrape.com/catalogue/"))
    i = i+1
    url = "http://books.toscrape.com/catalogue/category/books/fiction_10/page-" + str(i) + ".html"

with open("livre_category.csv", 'w') as file:
    for link in links:
        file.write(link + "\n")
