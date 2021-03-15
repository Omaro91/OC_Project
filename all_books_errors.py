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
info_all = []




def url_cat():  # Scrapping des URLS de toutes les catégories du site
    for ct in soup.find_all("ul", class_="nav nav-list"):
        for cti in ct.select("a"):
            ctg.append(URL_ALL + cti["href"])


def url_books():  # Scrapping des URLS des livres pour chaque catégorie
    for url in ctg[1:3]:

        i = 1
        url_m = url.replace("index.html", "page-" + str(i) + ".html")

        if requests.get(url_m).status_code == 200:
            while requests.get(url_m).status_code == 200:
                response_1 = requests.get(url_m)
                soup_1 = BeautifulSoup(response_1.content, "html.parser")

                for lien in soup_1.find_all("h3"):
                    liens = lien.a["href"]
                    links.append(liens.replace("../../../", URL_CTL))

                i = i + 1
                url_m = url.replace("index.html", "page-" + str(i) + ".html")

        else:
            response_2 = requests.get(url)
            soup_2 = BeautifulSoup(response_2.content, "html.parser")

            for lien in soup_2.find_all("h3"):
                liens = lien.a["href"]
                links.append(liens.replace("../../../", URL_CTL))

            for url3 in links:
                response_3 = requests.get(url3)
                soup_3 = BeautifulSoup(response_3.content, "html.parser")

                upc = soup_3.find("th", text="UPC").find_next("td").text

                title = soup_3.find("h1").text

                inc_tax = soup_3.find("th", text="Price (incl. tax)").find_next("td").text
                if inc_tax[0] == "£":
                    inc_tax_m = inc_tax[1:]
                else:
                    inc_tax_m = inc_tax[0] + " " + inc_tax[1:]

                exc_tax = soup_3.find("th", text="Price (excl. tax)").find_next("td").text
                if exc_tax[0] == "£":
                    exc_tax_m = exc_tax[1:]
                else:
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

                info = {
                    "product_page_url": url3,
                     "universal_product_code": upc,
                     "title": title, "price_including_tax": inc_tax_m,
                     "price_excluding_tax": exc_tax_m,
                     "number_available": num_m,
                     "product_description": desc_m,
                     "category": cat,
                     "review_rating": rev_m,
                     "image_url": image_url_m
                }

                info_all.append(info)
            links = []



csv_columns = ["product_page_url", "universal_product_code", "title", "price_including_tax", "price_excluding_tax",
               "number_available", "product_description", "category", "review_rating", "image_url"]


def save_csv():  # Enregistrement sur fichier CSV
    with open("all_books.csv", 'w', encoding="utf-8-sig") as AB:
        writer = csv.DictWriter(AB, fieldnames=csv_columns)
        writer.writeheader()
        for data in info_all:
            writer.writerow(data)


url_cat()  # Scrapping des URLS de toutes les catégories du site
url_books()  # Scrapping des URLS des livres pour chaque catégorie
save_csv()  # Enregistrement sur fichier CSV
