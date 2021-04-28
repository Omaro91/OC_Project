import requests
from bs4 import BeautifulSoup
import re
import csv
#  from word2number import w2n

URL_BTS = "http://books.toscrape.com/"
categories = []
books = []


def get_categories():  # Scrapping des URLS de toutes les catégories du site
    response_bts = requests.get(URL_BTS)
    soup_bts = BeautifulSoup(response_bts.content, 'html.parser')
    for ct in soup_bts.find_all("ul", class_="nav nav-list"):
        for cti in ct.select("a")[1:]:
            categories.append(URL_BTS + cti["href"])
    return categories


def get_books(category_url):  # Scrapping des URLS des livres pour chaque catégorie
    response_category = requests.get(category_url)
    soup_category = BeautifulSoup(response_category.content, 'html.parser')
    for long_book_url in soup_category.find_all("h3"):
        short_book_url = long_book_url.a["href"]
        books.append(short_book_url.replace("../../../", (URL_BTS + "catalogue/")))
    next_page = soup_category.find("li", class_="next")
    if next_page is not None:
        for a in soup_category.find("li", class_="next"):
            if a["href"] == "page-2.html":
                next_category_url = category_url[:-10] + a["href"]
            else:
                next_category_url = category_url[:-11] + a["href"]
            get_books(next_category_url)
    return books


def get_book_data(book_url):
    response_book = requests.get(book_url)
    soup_book = BeautifulSoup(response_book.content, "html.parser")

    upc = soup_book.find("th", text="UPC").find_next("td").text

    title = soup_book.find("h1").text

    inc_tax = soup_book.find("th", text="Price (incl. tax)").find_next("td").text
    inc_tax_m = inc_tax[1:]

    exc_tax = soup_book.find("th", text="Price (excl. tax)").find_next("td").text
    exc_tax_m = exc_tax[1:]

    num = soup_book.find("th", text="Availability").find_next("td").text
    num_m = re.findall(r'\d+', num)[0]
    #  other method : num_m = (num.split()[2])[1:]

    if soup_book.find("h2", text="Product Description") is not None:
        desc = soup_book.find("h2", text="Product Description").find_next("p").text
        desc_m = desc.replace(" ...more", "")
    else:
        desc_m = "NO DESCRIPTION AVAILABLE"

    cat = soup_book.find("li", class_="active").find_previous("a").text

    one_to_five = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }
    rev = soup_book.find("p", class_="star-rating")["class"][1]
    rev_m = (one_to_five[rev])
    #  other method : rev_m = w2n.word_to_num(rev)

    image_url = soup_book.find("div", class_="item active").find_next("img")["src"]
    image_url_m = image_url.replace("../../", URL_BTS)

    # Récupération de l'image
    image_alt = soup_book.find("div", class_="item active").find_next("img")["alt"]
    image_alt_m = re.sub("[\\\\/:*?\"<>|]", "", image_alt)

    with open('jpg/' + cat + "_" + image_alt_m + ".jpg", "wb") as img:
        img.write(requests.get(image_url_m).content)

    info = {
        "product_page_url": book_url,
        "universal_product_code": upc,
        "title": title, "price_including_tax": inc_tax_m,
        "price_excluding_tax": exc_tax_m,
        "number_available": num_m,
        "product_description": desc_m,
        "category": cat,
        "review_rating": rev_m,
        "image_url": image_url_m
    }
    return info


for category_csv in get_categories():
    response_csv = requests.get(category_csv)
    soup_csv = BeautifulSoup(response_csv.content, 'html.parser')
    category = soup_csv.find("li", class_="active").text
    # Ouvrir fichier csv
    with open('csv/' + category + '.csv', 'w', encoding='utf-8-sig') as csvfile:
        csv_columns = ["product_page_url", "universal_product_code", "title", "price_including_tax",
                       "price_excluding_tax", "number_available", "product_description", "category", "review_rating",
                       "image_url"]
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for book_csv in get_books(category_csv):
            data = get_book_data(book_csv)
            # Écrire une ligne dans le CSV
            writer.writerow(data)
            books = []
