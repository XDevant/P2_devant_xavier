from import_data import get_soup


def get_category_urls(url, base_url):
    """
    Arg: 
        String: site's URL
        String: the base URL needed to complete the relative path
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
            links.append(base_url + '/' + a['href'])
        except AttributeError:
            print(f"category link corrup: {a}")
    return links


def get_product_urls(url, base_product):
    """
    Arg: 
        String: URL of a book category
        String: the base URL needed to complete the relative path
    Return: 
        List of Strings: URLs of each product page in the category.
    """
    next =  True
    next_url = url
    urls = []
    while next:
        try:
            soup = get_soup(next_url).find('section')
            raw_links = soup.find('ol').findAll('li')
        except AttributeError:
            print(f"Unable to extract product urls for {url}")
            return urls
        for raw_link in raw_links:
            try:
                link = raw_link.find('a')['href']
            except (AttributeError):
                print(f"No url found: {raw_link}")
                continue
            product_url = base_product + link.split('..')[-1]
            urls.append(product_url)
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


def get_data(url, category, base_url):
    """
    Args:
        String: the URL of a product page.
        String: the book category of the product.
        String: the base URL needed to complete the relative path
    Return :
        (List of strings, String): the product data we were looking for
         and the url of the book cover image.
    """
    soup = get_soup(url)
    if soup is not None:
        soup = soup.find('article', {'class': 'product_page'})
    if soup is None:
        return([], '-')
    
    try:
        title = soup.find('h1').text
    except AttributeError:
        print(f"Title missing for {url} in {category}.csv")
        title = '-'
    
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
        tds = [td.text.strip('£') for td in tds[:4]]
    except (AttributeError, IndexError):
        print(f"Missing data in table: {url} in {category}.csv")
        tds = ['-', 0, 0, 0]
        
    description = soup.find('div', {'id': 'product_description'})
    try:
        description = description.find_next_sibling().text
    except AttributeError:
        print(f"Description missing for {url} in {category}.csv")
        description = '-'

    ratings = ['One', 'Two', 'Three', 'Four', 'Five']
    rating = '0'
    for i in range(5):
        if soup.find('p', {'class': ratings[i]}) is not None:
            rating =  str(i + 1)
            break
    
    img_url = '-'
    try:
        img_url = base_url + soup.find('img')['src'].split('..')[-1]
    except AttributeError:
        print(f"Image URL missing for {url} in {category}.csv")
    except IndexError:
        print(f"Corrupt image URL for {url} in {category}.csv")

    return ([url, tds[0], title, tds[2], tds[3], stock, description, category, rating, img_url], img_url)

