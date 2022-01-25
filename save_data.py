from os import makedirs
import pandas as pd
from import_data import get_url_content


def create_folders(csv_path, image_path):
    """
    Args:
        String: the path and name of the folder to create
        String: the path and name of the folder to create
    Creates folders to store data and images.
    Return: nothing
    """
    try:
        makedirs(csv_path, exist_ok=True)
        makedirs(image_path, exist_ok=True)
        return 1
    except Exception:
        print("Unable to create folders to save data !")
        return 0


def download_cover(url, image_path):
    """
    Arg:
        String: image url
        String: path of the target folder
    Download the image and save it in binary file
    Return
        Int: 1 for success 0 for failure
    """
    name = url.split('/')[-1]
    content = get_url_content(url)
    if content is not None:
        try:
            with open(f'{image_path}/{name}', 'wb') as file:
                file.write(content)
            return 1
        except Exception:
            print(f"Unable to save cover image for {name}")
    return 0


def save_to_csv(data_list, category, path, mode='a'):
    """
    Args:
        List of Strings (product data),
        String (book category = csv name)
    Kwarg:
        mode=String: "mode"='a' or 'w' (append) by default .
    mode='w' is used to create/overwrite the csv file with headers.
    Return
        Int: 1 for success 0 for failure
    """
    answer = 1
    name = f'{path}/{category}.csv'
    if len(data_list) == 0:
        data_list = ['-', '-', '-', 0, 0, 0, '-', category, 0, '-']
        answer = 0
    row = ("|".join(data_list) + "\n")
    try:
        with open(name, mode, encoding="utf-8") as f:
            f.write(row)
        return answer
    except Exception:
        return 0


def dfs_to_csv(error_dfs, path, name='error_log.csv'):
    """
    Args:
        List of Panda Dataframe
        String: the path of the folder where to save the df
    Kwargs:
        name=String : the name of the file to write in
    Concatenates the df and save the result in a csv
    Return:
        (int, int) : number of rows to save and saved
    """
    path_name = path.strip('\\')
    counted = -1
    saved = -1
    try:
        error_df = pd.concat(error_dfs)
        counted = error_df.shape[0]
        if counted == 0:
            return(0, 0)
    except Exception:
        print("Unable to oncat error df")
    else:
        try:
            error_df.to_csv(path + name, sep='|')
            print(f"An error log has been created in {path_name}")
            saved = counted
        except Exception:
            print(f"Unable to create an error log in {path_name}")
    return (counted, saved)
