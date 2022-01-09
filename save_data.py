from os import makedirs
import pandas as pd
from import_data import get_url_content


def create_folders(csv_path, image_path):
    """
    Args: No agr
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


def build_err_df(df, list_of_keys):
    """
    Args:
        Panda Dataframe
        dict: with keys used as column names to parse boolean data
    filters rows with errors in df
    Return: 
        Panda Dataframe: row of input df with errors
    """
    missing = True
    for key in list_of_keys:
        if missing:
            err_df = df[df[key] == True]
            missing = False
        else:
            err_df = pd.concat([err_df, df[df[key] == True]])
    return err_df.drop_duplicates()


def save_data_to_csv(data_list, name, mode='a'):
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
    try:
        with open(name, mode, encoding="utf-8") as f:
            f.write(row)
        return 1
    except Exception:
        print(f"Unable to save {row} in {name}")
        return 0
