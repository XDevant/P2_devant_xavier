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
        return BeautifulSoup(response.content, "html.parser")
    return None


def download_product_data(url, category):
    data = {}
    ratings = ['One', 'Two', 'Three', 'Four', 'Five']
    soup = get_soup(url).find('article', {'class': 'product_page'})
    main_soup = soup.find('div', {'class': 'product_main'})
    stock = main_soup.find('p', {'class': 'instock availability'})
    tds = soup.findAll('td')
    description = soup.find('div', {'id': 'product_description'})

    data[HEADERS[0]] = url
    data[HEADERS[1]] = tds[0].text
    data[HEADERS[2]] = main_soup.find('h1').text
    data[HEADERS[3]] = tds[2].text
    data[HEADERS[4]] = tds[3].text
    if stock is None:
        data[HEADERS[5]] = '0'
    else:
        data[HEADERS[5]] = stock.text.split('(')[1].split(' ')[0]
    data[HEADERS[6]] = description.find_next_sibling().text
    data[HEADERS[7]] = category
    data[HEADERS[8]] = '0'
    for i in range(5):
        if main_soup.find('p', {'class': ratings[i]}) is not None:
            data[HEADERS[8]] =  str(i + 1)
            break
    data[HEADERS[9]] = URL + soup.find('img')['src'].split('..')[-1]
    save_data_to_csv([data[header] for header in HEADERS], category)
    download_cover(data[HEADERS[9]])


def save_data_to_csv(data_list, category, append=True):
    row = "|".join(data_list) + "\n"
    if append:
        mode = 'a'
    else:
        mode = 'w'
    with open(f'data/csv/{category}.csv', mode) as file:
        file.write(row)


def download_cover(image_url):
    name = image_url.split('/')[-1]
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(f'data/img/{name}', 'wb') as file:
            file.write(response.content)


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
        save_data_to_csv(HEADERS, category, append=False)
        product_urls = get_product_urls(category_url)
        for product_url in product_urls:
            download_product_data(product_url, category)


if __name__ == "__main__":
    main_handler(URL)
