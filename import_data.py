import requests
import glob
from bs4 import BeautifulSoup

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
        if response.status_code == 200:
            return response.content
        else:
            print(f"Unable to fetch {url} code:{response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"Unable to fetch {url}: Site not found")
    except requests.exceptions.InvalidURL:
        print(f"Unable to fetch {url}: Invalid URL")
    except requests.exceptions.MissingSchema:
        print(f"Unable to fetch {url}: Not an URL")
    except requests.exceptions.ChunkedEncodingError:
        print(f"Connection broken while requesting {url}")
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


def get_files(csv_path, image_path):
    """
    Args: 
        String: the path to the files to extract
        String: the path to the files to extract
    Fetch the cover and csv files in the storage folders
    Return: a tuple of 2 lists of files(string)
    """
    try:
        img_files = glob.glob(image_path + "*.jpg")
        csv_files = glob.glob(csv_path + "*.csv")
        print(f"{len(img_files)} images files found in img folder")
        print(f"{len(csv_files)} CSV found in csv folder")
        return (csv_files, img_files)
    except Exception:
        print("Unable to find extrated data files")
        return ([], [])

