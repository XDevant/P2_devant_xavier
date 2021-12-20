import requests
from bs4 import BeautifulSoup


URL = "http://books.toscrape.com"
URL_PRODUCT = URL + '/catalogue'
"""Add /category/<category_n>/index.html where n, the category number,
 is it's index + 2  to reach product page 1.
Then replace index.html with page-<n>.html where <n> is the page number.
(20 books/page)
"""

# It is safe to append new columns at the end or to change names.
# It's unsafe to change column order or insert new ones (chk get_product_data())
HEADERS = ["product_page_url",
            "universal_ product_code",
            "title",
            "price_including_tax",
            "price_excluding_tax",
            "number_available",
            "product_description",
            "category",
            "review_rating",
            "image_url"]


def get_soup(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, features="html.parser")
    return None


def download_product_data(url, category):
    data_dict = {}

    save_data_to_csv([data_dict[header] for header in HEADERS], category)
    download_cover(data_dict[HEADERS[10]])


def save_data_to_csv(data_list, category):
    row = ",".join(data_list)
    with open(f'data/csv/{category}.csv', 'w') as file:
        file.write(row)


def download_cover(image_url):
    pass


def get_product_urls(url):
    next =  True
    next_url = url
    urls = []
    while next:
        soup = get_soup(next_url).find('section')
        links = [li.find('a') for li in soup.find('ol').findAll('li')]
        urls += [URL_PRODUCT + a['href'].split('..')[-1] for a in links]
        if soup.find('li', {'class': 'next'}) is None:
            next = False
        else:
            link = soup.find('li', {'class': 'next'}).find('a')['href']
            next_url = '/'.join(url.split('/')[:-1] + [link])
    return urls


def get_category_urls(url):
    soup = get_soup(url).find('ul', {'class': 'nav-list'}).findAll('a')
    urls = [URL + '/' + a['href'] for a in soup]
    return urls[1:]


def main_handler(site_url):
    category_urls = get_category_urls(site_url)
    for category_url in category_urls:
        category = category_url.split('_')[0].split('/')[-1]
        product_urls = get_product_urls(category_url)
        for product_url in product_urls:
            dowload_product_data(product_url, category)


if __name__ == "__main__":
    links = get_category_urls(URL)
    product0_links = get_product_urls(links[0])
    print(product0_links)
    product1_links = get_product_urls(links[1])
    print(product1_links)
