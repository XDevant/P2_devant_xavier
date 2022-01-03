from os import makedirs
import glob
import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = "http://books.toscrape.com"
URL_PRODUCT = URL + '/catalogue'

CSV_FOLDER = "Books-to-scrape\\CSV\\"
IMG_FOLDER = "Books-to-scrape\\Img\\"
""" Path of the folders where extracted data will be saved"""

RATINGS = ['One', 'Two', 'Three', 'Four', 'Five']
""" CSS selectors needed to extract ratings"""

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


def create_folders():
    """
    Args: No agr
    Creates folders to store data and images.
    Return: nothing
    """
    try:
        makedirs(CSV_FOLDER, exist_ok=True)
        makedirs(IMG_FOLDER, exist_ok=True)
        return 1
    except Exception:
        print("Unable to create folders to save data !")
        return 0


def get_url_content(url):
    """
    Arg:
        String: url 
    Given an page url, returns page content in a soup object.
    Return:
        String: HTML code of the requested page or None
    """
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        print(f"Unable to fetch {url}: Site not found")
        return None
    except requests.exceptions.InvalidURL:
        print(f"Unable to fetch {url}: Invalid URL")
        return None
    except requests.exceptions.MissingSchema:
        print(f"Unable to fetch {url}: Not an URL")
        return None
    except requests.exceptions.ChunkedEncodingError:
        print(f"Connection broken while requesting {url}") 
    if response.status_code == 200:
        return response.content
    print(f"Unable to fetch {url} code:{response.status_code}")
    return None


def get_soup(url):
    """
        Arg:
        String: url 
    Given an page url, returns page content in a soup object.
    Return:
        Soup object or None
    """
    content = get_url_content(url)
    if content is not None:
        try:
            return BeautifulSoup(content, "html.parser")
        except Exception:
           print(f"Unable to parse html for {url}")
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
    content = get_url_content(url)
    if content is not None:
        try:
            with open(f'{IMG_FOLDER}/{name}', 'wb') as file:
                file.write(content)
            return 1
        except Exception:
            print(f"Unable to save cover image for {name}")
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
    name = f'{CSV_FOLDER}/{category}.csv'
    try:
        with open(name, mode, encoding="utf-8") as f:
            f.write(row)
        return 1
    except Exception:
        print(f"Unable to save {row} in {name}")
        return 0


def get_product_data(url, category):
    """
    Args:
        String: the URL of a product page.
        String: the book category of the product.
    Return :
        (List of strings, String): the product data we were looking for
         and the url of the book cover image.
    """
    soup = get_soup(url)
    if soup is not None:
        soup = soup.find('article', {'class': 'product_page'})
    if soup is None:
        return('', '')
    
    try:
        title = soup.find('h1').text
    except AttributeError:
        print(f"Title missing for {url} in {category}.csv")
        title = ''
    
    stock = soup.find('p', {'class': 'instock availability'})
    if stock is None:
        stock = '0'
    else:
        try:
            stock = stock.text.split('(')[1].split(' ')[0]
        except IndexError:
            print(f"Unable to extract stocks: {url} in {category}.csv")
            stock = '0'
    
    tds = soup.findAll('td')
    try:
        tds = [td.text for td in tds[:4]]
    except (AttributeError, IndexError):
        print(f"Missing data in table: {url} in {category}.csv")
        tds = ['']*4
        
    description = soup.find('div', {'id': 'product_description'})
    try:
        description = description.find_next_sibling().text
    except AttributeError:
        print(f"Description missing for {url} in {category}.csv")
        description = ''
    
    ratings = '0'
    for i in range(5):
        if soup.find('p', {'class': RATINGS[i]}) is not None:
            ratings =  str(i + 1)
            break
    
    img_url = ''
    try:
        img_url = URL + soup.find('img')['src'].split('..')[-1]
    except AttributeError:
        print(f"Image URL missing for {url} in {category}.csv")
    except IndexError:
        print(f"Corrupt image URL for {url} in {category}.csv")

    return ([url, tds[0], title, tds[2], tds[3], stock, description, category, ratings, img_url], img_url)


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
        try:
            soup = get_soup(next_url).find('section')
            link_soup = soup.find('ol')
            links = link_soup.findAll('li')
        except AttributeError:
            print(f"Unable to extract product urls for {url}")
            return urls
        for link in links:
            li = link.find('a')
            try:
                product_url = URL_PRODUCT + li['href'].split('..')[-1]
                urls.append(product_url)
            except (AttributeError, IndexError):
                print(f"Corrupt product url: {li}")
        next_soup = soup.find('li', {'class': 'next'})
        if next_soup is None:
            next = False
        else:
            try:
                link = next_soup.find('a')['href']
                next_url = '/'.join(url.split('/')[:-1] + [link])
            except (AttributeError, IndexError):
                next = False
                print(f"Next page's URL not found:{next_url}")
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
    links_soup = soup.findAll('a')
    if len(links_soup) < 2:
        print(f"No link in nav container")
        return []
    links = []
    for a in links_soup[1:]:
        try:
            links.append(URL + '/' + a['href'])
        except AttributeError:
            print(f"category link corrup: {a}")
    return links


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

    create_folders()
    category_urls = get_category_urls(site_url)
    if len(category_urls) == 0:
        print(f"Unable to extract category pages urls. Scrapping aborted")
    for category_url in category_urls[:5]:
        category = category_url.split('_')[0].split('/')[-1]
        save_data_to_csv(HEADERS, category, mode = 'w')
        product_urls = get_product_urls(category_url)
        for product_url in product_urls:
            (data, image_url) = get_product_data(product_url, category)
            saved_data += save_data_to_csv(data, category)
            if data == '':
                print(f"No data for {product_url} in {category}.csv")
            if image_url == '':
                print(f"Image url not found for {product_url}")
            else:
                saved_img += download_cover(image_url)
    print(f"{len(category_urls)} extracted / 50")
    print(f"Successfuly saved {saved_data} / 1000 products into csv")
    print(f"Successfuly saved {saved_img} / 1000 images into files")

if __name__ == "__main__":
    main_handler(URL)
    img_files = glob.glob(IMG_FOLDER + "/" + "*.jpg")
    print(f"{len(img_files)} found in img folder")
    csv_files = glob.glob(CSV_FOLDER + "/" + "*.csv")
    print(f"{len(csv_files)} found in csv folder")
    for file in csv_files:
        df = pd.read_csv(file, delimiter="|")
        #df.info()
        #print(df.isna().sum())
        missing_data = df.isna().sum().sum()
        if missing_data > 0:
            print(f"{missing_data} missing_data in {file}")



