from re import sub
from re import compile as recompile
import os
from bs4 import BeautifulSoup

# titles
def parse_title_amazon(soup):
    titles = soup.find_all("span", class_="a-size-medium a-color-base a-text-normal")
    titles[:] = [title.get_text() for title in titles]
    titles_new = soup.find_all("span", class_="a-size-base-plus a-color-base a-text-normal")
    titles += [title.get_text() for title in titles_new]
    return titles


def parse_title_flipkart(soup):
    titles = soup.find_all("a", class_="s1Q9rs")
    titles[:] = [title.get_text() for title in titles]
    titles_new = soup.find_all("div", class_="_4rR01T")
    titles += [title.get_text() for title in titles_new]
    titles_new = soup.find_all("a", class_="IRpwTa")
    titles += [title.get_text() for title in titles_new]
    return titles


def parse_title_shopclues(soup):
    titles = soup.find_all('h2', class_="")
    titles[:] = [title.get_text() for title in titles]
    return titles


def parse_title_walmart(soup):
    titles = soup.find_all('span', class_="f6 f5-l normal dark-gray mb0 mt1 lh-title")
    titles[:] = [title.get_text() for title in titles]
    return titles


def parse_title_indiamart(soup):
    titles = soup.find_all("a", class_="prd-name")
    titles[:] = [title.get_text() for title in titles]
    return titles


def parse_title_alibaba(soup):
    titles = soup.find_all("p", class_="elements-title-normal__content large")
    titles[:] = [title.get_text() for title in titles]
    return titles


# images
def parse_image_amazon(soup):
    images = soup.find_all('img', {"class": "s-image"})
    images[:] = [image.get('src') for image in images]
    return images


def parse_image_flipkart(soup):
    images = soup.find_all('img', {"class": "_396cs4 _3exPp9"})
    images[:] = [image.get_text() for image in images]
    if len(images) < 5:
        images_new = soup.find_all('img', class_="_2r_T1I")
        images += [image.get('src') for image in images]
    if len(images) < 5:
        images_new = soup.find_all('img', class_="_396cs4 _2amPTt _3qGmMb        _3exPp9")
        images += [image.get('src') for image in images]
    if len(images) < 5:
        images += ["static/flipkart.jpeg"] * 5
    for i in range(len(images)):
        if images[i] == "":
            images[i] = "static/flipkart.jpeg"
    return images


def parse_image_shopclues(soup):
    images = soup.find_all("img", class_="")
    images[:] = [image.get('src') for image in images if len(image.get('src')) < 100]
    for i in range(len(images)):
        if images[i] == '':
            images[i] = "static/shopclues.jpeg"
    return images


def parse_image_walmart(soup):
    images = soup.find_all('a', class_="absolute w-100 h-100 z-1")
    images[:] = ["https://www.walmart.com" + str(image.get('href')) for image in images]
    for i in range(len(images)):
        if images[i] == "":
            images[i] = "static/walmart.jpeg"
    return images


def parse_image_indiamart(soup):
    images = soup.find_all("img", class_="prd-list-img cp ")
    images[:] = [image.get("src") for image in images]
    return images


def parse_image_alibaba(soup):
    images = soup.find_all("img", class_="J-img-switcher-item")
    images[:] = [image.get("src") for image in images]
    return images


# prices
def parse_price_amazon(soup):
    prices = soup.find_all('span', {'class': 'a-price-whole'})
    prices[:] = [price.get_text() for price in prices]
    return prices


def parse_price_flipkart(soup):
    prices = soup.find_all('div', {'class': '_30jeq3 _1_WHN1'})
    prices[:] = [price.get_text() for price in prices]
    if len(prices) < 5:
        prices_new = soup.find_all('div', {'class': '_30jeq3'})
        prices += [price.get_text() for price in prices_new]
    return prices


def parse_price_shopclues(soup):
    prices = soup.find_all('span', {'class': 'p_price'})
    prices[:] = [price.get_text().strip() for price in prices]
    return prices


def parse_price_walmart(soup):
    prices = soup.find_all('span', {'class': "f7 f6-l strike gray mr3"})
    prices[:] = [price.get_text() for price in prices]
    if len(prices) < 5:
        prices = [""] * 5
    return prices


def parse_price_indiamart(soup):
    prices = soup.find_all('span', class_="prc cp clr3 fwb fs18 prc cp")
    prices[:] = [price.get_text() for price in prices]
    return prices


def parse_price_alibaba(soup):
    prices = soup.find_all('span', class_="elements-offer-price-normal__promotion")
    prices[:] = [price.get_text() for price in prices]
    return prices


# URLs
def parse_url_amazon(soup):
    urls = soup.find_all('a', {"class": "a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"})
    urls[:] = ["https://www.amazon.in" + url.get('href') for url in urls]
    return urls


def parse_url_flipkart(soup):
    urls = soup.find_all('a', {'class': 's1Q9rs'})
    urls[:] = ["https://www.flipkart.com" + url.get('href') for url in urls]
    if len(urls) < 5:
        urls = soup.find_all('a', {'class': '_1fQZEK'})
        urls[:] = ["https://www.flipkart.com" + url.get('href') for url in urls]
    if len(urls) < 5:
        urls = soup.find_all('a', {'class': 'IRpwTa'})
        urls[:] = ["https://www.flipkart.com" + url.get('href') for url in urls]
    return urls


def parse_url_shopclues(soup):
    urls = soup.find_all("a")
    urls[:] = ["https:" + str(url.get('href')) for url in urls]
    return urls


def parse_url_walmart(soup):
    urls = soup.find_all('a', class_="product-title-link line-clamp line-clamp-2 truncate-title")
    urls[:] = [url.get('href') for url in urls]
    urls = ['https://www.walmart.com' + url for url in urls]
    return urls

def parse_url_alibaba(soup):
    urls = soup.find_all("a", class_="elements-title-normal__href")
    urls[:] = [url.get("href") for url in urls]
    return urls

def parse_url_indiamart(soup):
    urls = soup.find_all("a", class_="prd-name")
    urls[:] = [url.get("href") for url in urls]
    return urls
# ratings
def parse_rating_amazon(soup):
    ratings = soup.find_all("span", class_="a-icon-alt")
    ratings[:] = [sub('[^0-9.]', '', rating.get_text()) for rating in ratings]
    return ratings

def parse_rating_flipkart(soup):
    ratings = soup.find_all("div", class_="_3LWZlK")
    ratings[:] = [rating.get_text() for rating in ratings]
    if len(ratings) < 5:
        ratings_new = soup.find_all("div", class_="_3LWZlK _1BLPMq")
        ratings += [rating.get_text() for rating in ratings_new]
    return ratings

def parse_rating_shopclues(soup):
    ratings = soup.find_all("div", class_="ratings")
    ratings[:] = [rating.get_text().strip() for rating in ratings]
    return ratings

def parse_rating_walmart(soup):
    ratings = soup.find_all("span", class_="visuallyhidden")
    ratings[:] = [sub('[^0-9.]', '', rating.get_text()) for rating in ratings]
    if len(ratings) < 5:
        ratings = [""] * 5
    return ratings

def parse_rating_indiamart(soup):
    ratings = soup.find_all("div", class_="rI2i8A")
    ratings[:] = [rating.get_text() for rating in ratings]
    return ratings

def parse_rating_alibaba(soup):
    ratings = soup.find_all("div", class_="elements-offer-company__stars__grade")
    ratings[:] = [sub('[^0-9.]', '', rating.get_text()) for rating in ratings]
    return ratings
