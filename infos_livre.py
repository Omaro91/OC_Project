import requests
from bs4 import BeautifulSoup
import csv

csv_columns = ["product_page_url", "universal_product_code", "title", "price_including_tax", "price_excluding_tax",
               "number_available", "product_description", "category", "review_rating", "image_url"]

url = 'http://books.toscrape.com/catalogue/unicorn-tracks_951/index.html'

response = requests.get(url)  # code 200
response.encoding = 'UTF-8'  # a réglé les problèmes d'exportation csv
soup = BeautifulSoup(response.text, "lxml")  # affiche la page html

UPC = soup.find("th", text="UPC").find_next("td").text

title = soup.find("h1").text

inc_tax = soup.find("th", text="Price (incl. tax)").find_next("td").text[1:]

exc_tax = soup.find("th", text="Price (excl. tax)").find_next("td").text[1:]

num = soup.find("th", text="Availability").find_next("td").text
num_m = (num.split()[2])[1:]

desc = soup.find("h2", text="Product Description").find_next("p").text  # problème de caractères
desc_m = desc.replace(" ...more", "")

cat = soup.find("li", class_="active").find_previous("a").text

rev = soup.find("p", class_="star-rating")["class"][1]  # plus d'explication

image_url = soup.find("div", class_="item active").find_next("img")["src"]
image_url_m = image_url.replace("../..", "http://books.toscrape.com")

infos = [
    {"product_page_url": url, "universal_product_code": UPC, "title": title, "price_including_tax": inc_tax,
     "price_excluding_tax": exc_tax, "number_available": num_m, "product_description": desc_m, "category": cat,
     "review_rating": rev, "image_url": image_url_m}
]

print(infos)

csv_file = "infos_livre.csv"

with open(csv_file, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for data in infos:
        writer.writerow(data)
