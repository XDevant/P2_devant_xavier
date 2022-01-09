import pandas as pd
from import_data import get_files
from parse_data import get_category_urls
from parse_data import get_product_urls
from parse_data import get_product_data
from save_data import create_folders
from save_data import download_cover
from save_data import save_data_to_csv
from save_data import build_err_df
from check_data import read_error_dict
from check_data import check_headers
from check_data import build_error_dict

URL = "http://books.toscrape.com"
URL_PRODUCT = URL + '/catalogue'

BASE_FOLDER = "Books-to-scrape\\"
CSV_FOLDER = BASE_FOLDER + "CSV\\"
IMG_FOLDER = BASE_FOLDER + "Img\\"
""" Path of the folders where extracted data will be saved"""

HEADERS = ["product_page_url",
            "universal_product_code",
            "title",
            "price_including_tax",
            "price_excluding_tax",
            "number_available",
            "product_description",
            "category",
            "review_rating",
            "image_url"]


def main_handler(site_url):
    """
    Arg: String: site base url
        Control Flow function. Fetchs the category URLs, 
        then fetch each product URL to scrap the desired product data.
    Returns nothing.
    """
    saved_data = 0
    saved_img = 0

    create_folders(CSV_FOLDER, IMG_FOLDER)
    category_urls = get_category_urls(site_url, URL)
    if len(category_urls) == 0:
        print(f"Unable to extract category urls. Scrapping aborted")
    for category_url in category_urls:
        category = category_url.split('_')[0].split('/')[-1]
        csv_name = f'{CSV_FOLDER}/{category}.csv'
        save_data_to_csv(HEADERS, csv_name, mode = 'w')
        product_urls = get_product_urls(category_url, URL_PRODUCT)
        for product_url in product_urls:
            (data, image_url) = get_product_data(product_url, category, URL)
            if data == '':
                data = ['-', '-', '-', 0, 0, 0, '-', '-', 0, '-']
                print(f"No data for {product_url} in {category}.csv")
            saved_data += save_data_to_csv(data, csv_name)
            if image_url == '':
                print(f"Image url not found for {product_url}")
            else:
                saved_img += download_cover(image_url, IMG_FOLDER)
    print(f"{len(category_urls)} extracted / 50")
    print(f"Successfuly saved {saved_data} / 1000 products into csv")
    print(f"Successfuly saved {saved_img} / 1000 images into files")


def check_extracted_files():
    """
    Args: No Args
        Builds the console report and the list of df for each file
        where errors were found.
    Return: List of Panda Dataframes
    """
    result_dict = {
        'checked_files': 0,
        'perfect_files': 0,
        'checked_books': 0,
        'perfect_books': 0,
        'checked_covers': 0
        }
    expected_dict = {
        'checked_files': 50,
        'perfect_files': 48,
        'checked_books': 1000,
        'perfect_books': 998,
        'checked_covers': 1000
        }
    error_dfs = []

    csv_files, img_files = get_files(CSV_FOLDER, IMG_FOLDER)
    for file in csv_files:
        try:
            df = pd.read_csv(file, delimiter="|")
        except Exception:
            print(f"{file} is skipped: unable to read csv")
            continue
        try:
            check_file = check_headers(df, HEADERS, 'category', file)
        except Exception:
            check_file = False
        if check_file:
            result_dict['checked_files'] += 1
            book_count = df.shape[0]
            result_dict['checked_books'] += book_count
        else:
            print(f"{file} is skipped: columns or category mismatch")
            continue

        try:
            df, err_dict = build_error_dict(df, img_files, IMG_FOLDER)
        except Exception:
            print(f"{file} is skipped: unable to parse for errors")
            continue

        if err_dict['no_cover'] >= 0:
            result_dict['checked_covers'] += book_count 
            result_dict['checked_covers'] -= err_dict['no_cover']

        try:
            total_err, parsing_err = read_error_dict(err_dict, file)
        except Exception:
            print(f"{file} is skipped: unable to count errors")
            continue

        if total_err == 0 and parsing_err == 0:
            result_dict['perfect_files'] += 1
            result_dict['perfect_books'] += book_count
            continue

        if total_err > 0:
            err_df = build_err_df(df, err_dict.keys())
            try:
                log_len = len(err_df)
            except Exception:
                log_len = 0
            else:
                print(f"{log_len} rows will be added to error_logs")
                error_dfs.append(err_df)
            if parsing_err == 0 and log_len > 0:
                result_dict['perfect_books'] += book_count - log_len

    for key, value in result_dict.items():
        print(f"{key}: {value} (expected : {expected_dict[key]})")
    return error_dfs


if __name__ == "__main__":

    main_handler(URL)

    error_dfs = check_extracted_files()

    if len(error_dfs) > 0:
        try:
            error_df = pd.concat(error_dfs)
            error_df.to_csv(BASE_FOLDER +"error_log.csv", sep='|')
            print(f"An error log has been created in {BASE_FOLDER}")
        except Exception:
            print(f"Unable to create an error log in {BASE_FOLDER}")
        else:
            if len(error_df) == 2:
                print("2 errors detected and reported as expexted")
                print(f"(2 description are missing on {URL})")

