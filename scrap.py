import pandas as pd
from import_data import get_files
from parse_data import get_category_urls
from parse_data import get_product_urls
from parse_data import get_data
from save_data import create_folders
from save_data import download_cover
from save_data import save_to_csv
from save_data import build_err_df
from save_data import dfs_concat_to_csv
from check_data import check_headers
from check_data import build_error_dict
from display_data import plural
from display_data import read_error_dict
from display_data import print_result
from display_data import print_note

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
    Return:
        Dict: with only int values: the result dict
    """
    saved_data = 0
    saved_img = 0
    result_dict = {
        'csv_file': 0,
        'saved_line': 0,
        'saved_image': 0,
        'product_error': 0,
        'image_error': 0,
        'category_error': 0
        }
    
    create_folders(CSV_FOLDER, IMG_FOLDER)
    category_urls = get_category_urls(site_url, URL)
    if len(category_urls) == 0:
        print(f"Unable to extract category urls. Scrapping aborted")
        return result_dict
    for category_url in category_urls:
        category = category_url.split('_')[0].split('/')[-1]
        name = f'{CSV_FOLDER}/{category}.csv'
        check = save_to_csv(HEADERS, name, mode = 'w')
        if check == 0:
            print(f"Unable to create CSV file for category {category}")
            result_dict['category_error'] += 1
            continue
        product_urls = get_product_urls(category_url, URL_PRODUCT)
        if product_urls == []:
            print(f"No product URL found for category {category}")
            result_dict['category_error'] += 1
            continue
        for product_url in product_urls:
            (data, image_url) = get_data(product_url, category, URL)
            saved = save_to_csv(data, name)
            result_dict['saved_line'] += saved
            if saved == 0:
                if data == []:
                    print(f"Data not found for {product_url}")
                else:
                    print(f"Data not saved for {product_url}")
                result_dict['product_error'] += 1
            if image_url != '-':
                downloaded = download_cover(image_url, IMG_FOLDER)
                result_dict['saved_image'] += downloaded
            else:
                downloaded = 0
            if downloaded == 0:
                result_dict['image_error'] += 1
                print(f"Image url not found for {product_url}")
        result_dict['csv_file'] += 1
        print(f"Category {category} saved in {category}.csv")
    return result_dict


def check_extracted_files():
    """
    Args: No Args
        Builds the console report and the list of df for each file
        where errors were found.
    Return:
        Dict: with only int values: the result dict
    """
    result_dict = {
        'checked_file': 0,
        'perfect_file': 0,
        'checked_book': 0,
        'perfect_book': 0,
        'checked_cover': 0,
        'readcsv_error': 0,
        'mismatch_error': 0,
        'parsing_failed_error': 0,
        'files_with_parsing_error': 0,
        'total_parsing_error': 0,
        'files_with_data_error': 0,
        'total_data_error': 0
        }
    error_dfs = []

    print(f"    Scaning Data Folders")
    csv_files, img_files = get_files(CSV_FOLDER, IMG_FOLDER)
    print(f"    Scaning CSV for inaccurate data")
    for file in csv_files:
        try:
            df = pd.read_csv(file, delimiter="|")
        except Exception:
            print(f"{file} is skipped: unable to read csv")
            result_dict['readcsv_error'] += 1
            continue
        try:
            check_file = check_headers(df, HEADERS, 'category', file)
        except Exception:
            check_file = False
        if check_file:
            result_dict['checked_file'] += 1
            book_count = df.shape[0]
            result_dict['checked_book'] += book_count
        else:
            print(f"{file} is skipped: columns or category mismatch")
            result_dict['mismatch_error'] += 1
            continue
        numeric = [3, 4, 5, 8]
        for col in numeric:
            df[HEADERS[col]].fillna(0, inplace=True)
        df.fillna('-', inplace=True)
        try:
            df, err_dict = build_error_dict(df, img_files, IMG_FOLDER)
        except Exception:
            print(f"{file} is skipped: unable to parse errors")
            result_dict['parsing_failed_error'] += 1
            continue

        total_err, parsing_err = read_error_dict(err_dict, file)
        if parsing_err > 0:
            result_dict['files_with_parsing_error'] += 1
            result_dict['total_parsing_error'] += parsing_err
        if total_err > 0:
            result_dict['files_with_data_error'] += 1
            result_dict['total_data_error'] += total_err
        if err_dict['no_cover'] >= 0:
            result_dict['checked_cover'] += book_count
            result_dict['checked_cover'] -= err_dict['no_cover']
        if total_err == 0 and parsing_err == 0:
            result_dict['perfect_file'] += 1
            result_dict['perfect_book'] += book_count
            continue
        if total_err > 0:
            err_df = build_err_df(df, err_dict.keys())
            try:
                n = len(err_df)
            except Exception:
                n = 0
            else:
                print(f"{n} row{plural(n)} will be added to error_log")
                error_dfs.append(err_df)
            if parsing_err == 0 and n > 0:
                result_dict['perfect_book'] += book_count - n

    counted, saved = dfs_concat_to_csv(error_dfs, BASE_FOLDER)
    expected = 2
    print_note(counted, saved, expected, URL)
    return result_dict


if __name__ == "__main__":
    expected_main = {
        'csv_file': 50,
        'saved_line': 1000,
        'saved_image': 1000,
        'product_error': 0,
        'image_error': 0,
        'category_error': 0
        }
    expected_check = {
        'checked_file': 50,
        'perfect_file': 48,
        'checked_book': 1000,
        'perfect_book': 998,
        'checked_cover': 1000,
        'readcsv_error': 0,
        'mismatch_error': 0,
        'parsing_failed_error': 0,
        'files_with_parsing_error': 0,
        'total_parsing_error': 0,
        'files_with_data_error': 2,
        'total_data_error': 2
        }
    
    print(f"\n      *** Starting Extraction ***")
    result_dict = main_handler(URL)
    print(f"\n      *** Extraction Results: ***")
    print_result(result_dict, expected=expected_main)
    print(f"\n      *** Checking Extracted Data ***")
    result_dict = check_extracted_files()
    print(f"\n      *** Check Results: ***")
    print_result(result_dict, expected=expected_check)
    print('\n')


