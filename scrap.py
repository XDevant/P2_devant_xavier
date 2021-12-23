import requests
from bs4 import BeautifulSoup


URL = "http://books.toscrape.com"
URL_PRODUCT = URL + '/catalogue'

RATINGS = ['One', 'Two', 'Three', 'Four', 'Five']

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
    """
    Arg:
        String: url 
    Given an page url, returns page content in a soup object.
    Return:
        Soup object or None
    """
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, "html.parser")
    print(f"Unable to fetch {url} code:{response.status_code}")
    return None


def download_cover(url):
    """
    Arg:
        String: image url 
    Download the image and save it in binary file 
    Return
        Int: 1 for success 0 for failure
    """
    name = url.split('/')[-1]
    response = requests.get(url)
    if response.status_code == 200:
        with open(f'data/img/{name}', 'wb') as file:
            file.write(response.content)
        return 1
    print(f"Unable to fetch image: {url} code:{response.status_code}")
    return 0


def save_data_to_csv(data_list, category, mode='a'):
    """
    Args:
        List of Strings (product date),
        String (book category = csv name)
    Kwarg:
        mode=String: "mode"='a' or 'w' (append) by default .
    mode='w' is used to create/overwrite the csv file with headers.
    Return
        Int: 1 for success 0 for failure
    """
    row = ("|".join(data_list) + "\n")
    with open(f'data/csv/{category}.csv', mode, encoding="utf-8") as f:
        f.write(row)
    return 1


def get_product_data(url, category):
    """
    Args:
        String: the URL of a product page.
        String: the book category of the product.
    Return :
        List of strings: the product data we were looking for.
    """
    soup = get_soup(url)
    if soup is None:
        return('', '')
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
        print(f"Missing data in table: {url} in {category}.csv")
        tds = ['']*4
    else:
        tds = [td.text for td in tds[:4]]
    try:
        description = soup.find('div', {'id': 'product_description'})
        description = description.find_next_sibling().text
    except AttributeError:
        print(f"Description missing for {url} in {category}.csv")
        description = ''
    ratings = '0'
    for i in range(5):
        if main_soup.find('p', {'class': RATINGS[i]}) is not None:
            ratings =  str(i + 1)
            break
    img_url = URL + soup.find('img')['src'].split('..')[-1]

    return [url, tds[0], title, tds[2], tds[3], stock, description, category, ratings, img_url]


def get_product_urls(url):
    """
    Arg: 
        String: URL of a book category
    Return: 
        List of Strings: URLs of each product page in the category.
    """
    next =  True
    next_url = url
    urls = []
    while next:
        soup = get_soup(next_url).find('section').find('ol')
        if soup is None:
            return []
        links = soup.findAll('li')
        for link in links:
            li = link.find('a')
            product_url = URL_PRODUCT + li['href'].split('..')[-1]
            urls.append(product_url)
        next_soup = soup.find('li', {'class': 'next'})
        if next_soup is None:
            next = False
        else:
            link = next_soup.find('a')['href']
            next_url = '/'.join(url.split('/')[:-1].append(link))
    return urls


def get_category_urls(url):
    """
    Arg: 
        String: site's URL
    Return: 
        List of Strings: URLs of each category index page.
    """
    soup = get_soup(url)
    if soup is None:
        return []
    soup = soup.find('ul', {'class': 'nav-list'})
    if soup is None:
        print(f"Unable to find nav container")
        return []
    links = soup.findAll('a')
    if len(links) < 2:
        print(f"No link in nav container")
        return []
    return [URL + '/' + a['href'] for a in links[1:]]


def main_handler(site_url):
    """
    Arg:
        String: site base url
    Control Flow function. Fetchs the category URLs, 
    then fetch each product URL to scrap the desired product data.
    Returns nothing.
    """
    saved_data = 0
    saved_img = 0

    category_urls = get_category_urls(site_url)
    for category_url in category_urls:
        category = category_url.split('_')[0].split('/')[-1]
        save_data_to_csv(HEADERS, category, mode = 'w')
        product_urls = get_product_urls(category_url)
        for product_url in product_urls:
            (data, image_url) = get_product_data(product_url, category)
            save_data_to_csv(data, category)
            if data == '':
                print(f"Data not found for {product_url} in {category}.csv")
            else:
                saved_data += 1
            if image_url == '':
                print(f"Image url not found for {product_url}")
            else:
                saved_img += download_cover(image_url)
    print(f"Successfuly saved {saved_data} / 1000 products into csv")
    print(f"Successfuly saved {saved_img} / 1000 images into files")

if __name__ == "__main__":
    main_handler(URL)
