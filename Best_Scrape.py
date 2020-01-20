### This is a webscraper for the website "Best Buy" where you can extract
### data on a product. This program only records product name, price, ratings,
### whether the item is on sale, model/sku information and the product's url.


#uses libaries request and BeautifulSoup to webscrape
import requests
import bs4
import math
from bs4 import BeautifulSoup as soup
#creates new urls depending on what product you're searching for
#for product search, every space in string should be replaced with %20

page_num = 1
product_search = "polaroid%20camera"
max_pages = 1

def create_url(page_num,product_search):
    return 'https://www.bestbuy.com/site/searchpage.jsp?cp=' + str(page_num) + '&st=' + str(product_search)

#extracts data from specfic webpage at bestbuy and records it in csv file
def record_data(file, page_data):
    # Iterate through the page
    for container in page_data:
        # Checks if item is sold out, if sold out it doesn't include in csv
        sold_out = container.findAll("button", {"class": "btn btn-disabled btn-sm btn-block add-to-cart-button"})
        if sold_out:
            continue

        # Filters out product name
        title_container = container.findAll("h4", {"class": "sku-header"})
        product_name = title_container[0].text.replace(",", "")

        # Filters out product url
        product_url = "https://www.bestbuy.com" + container.a["href"]

        # Filters out price of product
        price_container = container.findAll("span", {"class": "sr-only"})
        product_price = price_container[0].text.strip("Your price for this item is ").replace(",","")

        # Filter out ratings
        rating_container = container.find("div", {"class": "c-ratings-reviews-v2 ugc-ratings-reviews v-small"})
        product_rating = rating_container.i["alt"]
        if product_rating == "0":
            product_number = "Not Yet Rated"
        else:
            number_review = container.find("span", {"class": "c-total-reviews"})
            product_number = number_review.text.strip().strip("()").replace("," , "")

        # Filters out model number and sku
        model_container = container.findAll("div", {"class": "sku-attribute-title"})
        if model_container:
            product_model = model_container[0].text
            product_sku = model_container[1].text
        else:
            product_model = "Not Listed"
            product_sku = "Not Listed"

        # Filter out if sale ongoing
        sale_container = container.findAll("div", {"class": "pricing-price__savings"})
        if sale_container:
            product_sale = "Yes " + sale_container[0].text
        else:
            product_sale = "No"

        #Write all data to csv file
        file.write(product_name + "," + product_price + "," + product_rating + "," + product_number
                   + "," + product_model + "," + product_sku + "," + product_sale + "," + product_url + "\n")

#loops through all pages with the specified search item name
def total_data(file, product_search,max_pages):
    for i in range(max_pages):
        my_url = create_url(i+1,product_search)
        page_html = requests.get(my_url, headers=headers)
        page_soup = soup(page_html.text, "html.parser")
        containers = page_soup.findAll("div", {"class":"shop-sku-list-item"})
        record_data(file, containers)


#this header is used to emulate a browser that is looking at the page
#change filename if you wish to store it elsewhere
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
filename = "Best_products.csv"

#Set up csv for writing
f = open(filename, "w")
csv_header = "Product Name, Price, Rating, Number of Reviews, Model, SKU, On Sale?, URL\n"
f.write(csv_header)

#opening page and connecting
page_html = requests.get(create_url(1, product_search), headers=headers)

#html parsing
page_soup = soup(page_html.text, "html.parser")

#grabs each product and separates them by containers
containers = page_soup.findAll("div", {"class":"shop-sku-list-item"})

#Calculates number of pages of results as there are 25 results on a standard page
item_count = page_soup.find("span", {"class" : "item-count"})
max_pages = math.ceil(int(item_count.text.strip("items"))/25)

#runs the webscraper function and records relevant data in csv
total_data(f, product_search, max_pages)

f.close()