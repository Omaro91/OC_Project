import requests
from bs4 import BeautifulSoup
import re
import csv

#  from word2number import w2n

URL_ALL = "http://books.toscrape.com/"
response = requests.get(URL_ALL)
soup = BeautifulSoup(response.content, 'html.parser')

URL_CTL = "http://books.toscrape.com/catalogue/"
ctg = []
links = []


def get_categories():  # Scrapping des URLS de toutes les catégories du site
    for ct in soup.find_all("ul", class_="nav nav-list"):
        for cti in ct.select("a")[1:]:
            ctg.append(URL_ALL + cti["href"])
    return ctg


def get_books(category_url):  # Scrapping des URLS des livres pour chaque catégorie
    response_cat = requests.get(category_url)
    soup_cat = BeautifulSoup(response_cat.content, "html.parser")
    for lien in soup_cat.find_all("h3"):
        liens = lien.a["href"]
        links.append(liens.replace("../../../", URL_CTL))
        i = 2
        while soup_cat.find("li", class_="next") is not None:
            category_url_m = category_url.replace("index.html", "page-" + str(i) + ".html")
            get_books(category_url_m)
            links.extend(category_url_m)
            i = i + 1
    print(links)
    return links


def get_book_data(book_url):  # Scrapping des détails pour chaque livre

    response_3 = requests.get(book_url)
    soup_3 = BeautifulSoup(response_3.content, "html.parser")

    upc = soup_3.find("th", text="UPC").find_next("td").text

    title = soup_3.find("h1").text

    inc_tax = soup_3.find("th", text="Price (incl. tax)").find_next("td").text
    inc_tax_m = inc_tax[0] + " " + inc_tax[1:]

    exc_tax = soup_3.find("th", text="Price (excl. tax)").find_next("td").text
    exc_tax_m = exc_tax[0] + " " + exc_tax[1:]

    num = soup_3.find("th", text="Availability").find_next("td").text
    num_m = re.findall(r'\d+', num)[0]
    #  other method : num_m = (num.split()[2])[1:]

    if soup_3.find("h2", text="Product Description") is not None:
        desc = soup_3.find("h2", text="Product Description").find_next("p").text
        desc_m = desc.replace(" ...more", "")
    else:
        desc_m = "NO DESCRIPTION AVAILABLE"

    cat = soup_3.find("li", class_="active").find_previous("a").text

    one_to_five = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    rev = soup_3.find("p", class_="star-rating")["class"][1]
    rev_m = (one_to_five[rev])
    #  other method : rev_m = w2n.word_to_num(rev)

    image_url = soup_3.find("div", class_="item active").find_next("img")["src"]
    image_url_m = image_url.replace("../../", URL_ALL)

    img_data = requests.get(image_url_m).content

    info = [
        {"product_page_url": book_url,
         "universal_product_code": upc,
         "title": title, "price_including_tax": inc_tax_m,
         "price_excluding_tax": exc_tax_m,
         "number_available": num_m,
         "product_description": desc_m,
         "category": cat,
         "review_rating": rev_m,
         "image_url": image_url_m}
    ]
    return info


csv_columns = ["product_page_url", "universal_product_code", "title", "price_including_tax", "price_excluding_tax",
               "number_available", "product_description", "category", "review_rating", "image_url"]

for category_url in get_categories():
    # Ouvrir fichier csv
    with open("all_books.csv", 'w', encoding="utf-8-sig") as AB:
        writer = csv.DictWriter(AB, fieldnames=csv_columns)
        writer.writeheader()
    for book_url in get_books(category_url):
        data = get_book_data(book_url)
        writer.writerow(data)
