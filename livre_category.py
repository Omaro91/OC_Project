import requests
from bs4 import BeautifulSoup
from word2number import w2n
import csv

url = "http://books.toscrape.com/catalogue/category/books/mystery_3/index.html"
links = []
i = 1
url_m = url.replace("index.html", "page-"+str(i)+".html")
if str(requests.get(url_m)) == "<Response [200]>":
    while str(requests.get(url_m)) == "<Response [200]>":
        print("Page num°:", i)
        response = requests.get(url_m)  # code 200
        response.encoding = 'UTF-8'  # a réglé les problèmes d'exportation csv
        soup = BeautifulSoup(response.text, "lxml")  # affiche la page html
        for lien in soup.find_all("h3"):
            liens = lien.a["href"]
            print(liens.replace("../../../", "http://books.toscrape.com/catalogue/"))
            links.append(liens.replace("../../../", "http://books.toscrape.com/catalogue/"))
        i = i+1
        url_m = url.replace("index.html", "page-" + str(i) + ".html")
else:
    print("Page num°:", i)
    response = requests.get(url)  # code 200
    response.encoding = 'UTF-8'  # a réglé les problèmes d'exportation csv
    soup = BeautifulSoup(response.text, "lxml")  # affiche la page html
    for lien in soup.find_all("h3"):
        liens = lien.a["href"]
        print(liens.replace("../../../", "http://books.toscrape.com/catalogue/"))
        links.append(liens.replace("../../../", "http://books.toscrape.com/catalogue/"))
print(len(links))

csv_columns = ["product_page_url", "universal_product_code", "title", "price_including_tax", "price_excluding_tax",
               "number_available", "product_description", "category", "review_rating", "image_url"]
infos = []
for url3 in links:

    response = requests.get(url3)  # code 200
    response.encoding = 'UTF-8'  # a réglé les problèmes d'exportation csv
    soup = BeautifulSoup(response.text, "lxml")  # affiche la page html

    upc = soup.find("th", text="UPC").find_next("td").text

    title = soup.find("h1").text

    inc_tax = soup.find("th", text="Price (incl. tax)").find_next("td").text

    exc_tax = soup.find("th", text="Price (excl. tax)").find_next("td").text

    num = soup.find("th", text="Availability").find_next("td").text
    num_m = (num.split()[2])[1:]

    desc = soup.find("h2", text="Product Description").find_next("p").text  # problème de caractères
    desc_m = desc.replace(" ...more", "")

    cat = soup.find("li", class_="active").find_previous("a").text

    rev = soup.find("p", class_="star-rating")["class"][1]
    rev_m = w2n.word_to_num(rev)

    image_url = soup.find("div", class_="item active").find_next("img")["src"]
    image_url_m = image_url.replace("../..", "http://books.toscrape.com")

    info = [
        {"product_page_url": url, "universal_product_code": upc, "title": title, "price_including_tax": inc_tax,
         "price_excluding_tax": exc_tax, "number_available": num_m, "product_description": desc_m, "category": cat,
         "review_rating": rev_m, "image_url": image_url_m}
    ]
    infos.append(info)

with open("livre_category.csv", 'w') as csvfile:

    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for data2 in infos:
        for data in data2:
            writer.writerow(data)
