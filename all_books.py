import requests
from bs4 import BeautifulSoup
from word2number import w2n
import csv

URLB = "http://books.toscrape.com/"
response = requests.get(URLB)

soup = BeautifulSoup(response.content, 'html.parser')

INDEX = "http://books.toscrape.com/catalogue/"
ctg = []
links = []
infos = []
for ct in soup.find_all("ul", class_="nav nav-list"):
    for cti in ct.select("a"):
        ctg.append(URLB + cti["href"])

for url in ctg[1:]:

    i = 1
    url_m = url.replace("index.html", "page-"+str(i)+".html")

    if requests.get(url_m).status_code == 200:
        while requests.get(url_m).status_code == 200:

            response = requests.get(url_m)

            soup = BeautifulSoup(response.content, "html.parser")
            for lien in soup.find_all("h3"):
                liens = lien.a["href"]
                links.append(liens.replace("../../../", INDEX))
            i = i+1
            url_m = url.replace("index.html", "page-" + str(i) + ".html")
    else:

        response = requests.get(url)

        soup = BeautifulSoup(response.content, "html.parser")
        for lien in soup.find_all("h3"):
            liens = lien.a["href"]
            links.append(liens.replace("../../../", INDEX))

csv_columns = ["product_page_url", "universal_product_code", "title", "price_including_tax", "price_excluding_tax",
               "number_available", "product_description", "category", "review_rating", "image_url"]

for url3 in links:

    response = requests.get(url3)

    soup = BeautifulSoup(response.content, "html.parser")

    upc = soup.find("th", text="UPC").find_next("td").text

    title = soup.find("h1").text

    inc_tax = soup.find("th", text="Price (incl. tax)").find_next("td").text

    exc_tax = soup.find("th", text="Price (excl. tax)").find_next("td").text

    num = soup.find("th", text="Availability").find_next("td").text
    num_m = (num.split()[2])[1:]

    if soup.find("h2", text="Product Description") is not None:
        desc = soup.find("h2", text="Product Description").find_next("p").text
        desc_m = desc.replace(" ...more", "")
    else:
        desc_m = ""

    cat = soup.find("li", class_="active").find_previous("a").text

    rev = soup.find("p", class_="star-rating")["class"][1]
    rev_m = w2n.word_to_num(rev)

    image_url = soup.find("div", class_="item active").find_next("img")["src"]
    image_url_m = image_url.replace("../../", URLB)

    info = [
        {"product_page_url": url3,
         "universal_product_code": upc,
         "title": title, "price_including_tax": inc_tax,
         "price_excluding_tax": exc_tax,
         "number_available": num_m,
         "product_description": desc_m,
         "category": cat,
         "review_rating": rev_m,
         "image_url": image_url_m}
    ]
    infos.append(info)

with open("all_books.csv", 'w', encoding="utf-8-sig") as csvfile:

    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for data2 in infos:
        for data in data2:
            print(data)
            writer.writerow(data)
