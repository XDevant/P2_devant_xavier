import requests
from bs4 import BeautifulSoup


URL = "http://books.toscrape.com"
URL_PRODUCT = URL + '/catalogue'

RATINGS = ['One', 'Two', 'Three', 'Four', 'Five']

# It is safe to append new columns at the end or to change names.
# It's unsafe to change any column index (chk download_product_data())
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
    """Given an page url, returns page content in a soup object.
    If http request fails, return None
    """
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, "html.parser")
    print(f"Unable to fetch url:{url} response code:{response.status_code}")
    return None


def download_cover(url):
    """Take a image URL as parameter.
    Download the image and save it in binary file 
    or print an error message.
    Return nothing
    """
    name = url.split('/')[-1]
    response = requests.get(url)
    if response.status_code == 200:
        with open(f'data/img/{name}', 'wb') as file:
            file.write(response.content)
    else:
        print(f"Unable to fetch url:{url} code:{response.status_code}")


def save_data_to_csv(data_list, category, mode='a'):
    """Takes a product's list of data as first parameter.
    The book category in second parameter is the csv name.
    The "mode" kwarg is set to 'a' (append) by default .
    mode='w' is only used to create/overwrite the csv file and 
    write the headers on first line.
    Returns nothing.
    """
    row = ("|".join(data_list) + "\n")
    with open(f'data/csv/{category}.csv', mode, encoding="utf-8") as file:
        file.write(row)


def download_product_data(url, category):
    """The first parameter is the URL of a product.
    The second parameter is the only data to save we have for now.
    Return a list of data ordered thanks to the HEADERS global constant
    and the URL of the book cover image in a tuple.
    """
    data = {}
    soup = get_soup(url)
    if soup is None:
        return('\n', '')
    soup = soup.find('article', {'class': 'product_page'})
    main_soup = soup.find('div', {'class': 'product_main'})

    title = main_soup.find('h1').text
    stock = main_soup.find('p', {'class': 'instock availability'})
    if stock is None:
        stock = '0'
    else:
        stock = stock.text.split('(')[1].split(' ')[0]
    tds = soup.findAll('td')
    if tds is None or (len(tds) < 4):
        print(f"tds too short, missing data in table for product at URL {url} in {category}.csv")
        tds = ['']*4
    else:
        tds = [td.text for td in tds[:4]]
    try:
        description = soup.find('div', {'id': 'product_description'})
        description = description.find_next_sibling().text
    except AttributeError:
        print(f"Description missing or not found for product at URL {url} in {category}.csv")
        description = ''
    ratings = '0'
    for i in range(5):
        if main_soup.find('p', {'class': RATINGS[i]}) is not None:
            ratings =  str(i + 1)
            break
    img_url = URL + soup.find('img')['src'].split('..')[-1]

    data[HEADERS[0]] = url
    data[HEADERS[1]] = tds[0]
    data[HEADERS[2]] = title
    data[HEADERS[3]] = tds[2]
    data[HEADERS[4]] = tds[3]
    data[HEADERS[5]] = stock
    data[HEADERS[6]] = description
    data[HEADERS[7]] = category
    data[HEADERS[8]] = ratings
    data[HEADERS[9]] = img_url
    return ([data[header] for header in HEADERS], img_url)


def get_product_urls(url):
    """Takes a category index page URL as parameter.
    Return a list of each product's URL in the caterogy.
    """
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
    """Given the site's URL, return a list of URLs with each 
    category index page.
    """
    soup = get_soup(url).find('ul', {'class': 'nav-list'}).findAll('a')
    urls = [URL + '/' + a['href'] for a in soup]
    return urls[1:]


def main_handler(site_url):
    """Control Flow function. Given the site URL, fetchs the category URLs to 
    then fetch each product URL to scrap the desired product data.
    Returns nothing.
    """
    saved_data = 0
    saved_img = 0

    category_urls = get_category_urls(site_url)
    for category_url in category_urls[:6]:
        category = category_url.split('_')[0].split('/')[-1]
        save_data_to_csv(HEADERS, category, mode = 'w')
        product_urls = get_product_urls(category_url)
        for product_url in product_urls:
            (data, image_url) = download_product_data(product_url, category)
            save_data_to_csv(data, category)
            if data == '\n':
                print(f"Data not found for {product_url} line skipped in {category}.csv")
            else:
                saved_data += 1
            if image_url == '':
                print(f"Image url not found for {product_url}")
            else:
                download_cover(image_url)
                saved_img += 1
    print(f"Successfuly saved {saved_data} out of 1000 products data into csv files")
    print(f"Successfuly saved {saved_img} out of 1000 images into files")

if __name__ == "__main__":
    main_handler(URL)
