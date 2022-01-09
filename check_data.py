def read_error_dict(err_dict, file):
    """
    Args:
        dict with int values
        String: file name
    Count errors and prints then on the console
    Return: 
        (Int, Int) : individual and global error counts
    """
    total_errors = 0
    parsing_errors = 0
    for key, value in err_dict.items():
        if value == -1:
            print(f"Unable to parse books with {key} in {file}")
            parsing_errors += 1
        if value > 0:
            total_errors += value
            print(f"{value} book with {key} in {file}")
    return (total_errors, parsing_errors)


def check_headers(df, headers, col, file):
    """
    Args:
        Panda Dataframe
        List of Strings : headers 
        String : column name
        String : file name
    Check if df columns names match headers
    Check if name in file match the value in df[col]
    and if that value is unique
    Return: Boolean
    """
    h_ok = all(i == j for i, j in zip(df.columns.tolist(),  headers))
    name = file.split('\\')[-1].split('.')[0]
    category_df = df[col].unique()
    category_ok = category_df.shape[0] == 1 and category_df[0] == name
    return h_ok and category_ok


def build_error_dict(df, img_files, img_path):
    """
    Args:
        Panda Dataframe
        List of String (file names)
    
    Return: 
        (Panda Dataframe, Dict)
    """
    err_dict = {}
    if 'float' in str(df['price_including_tax'].dtypes):
        df['no_tax'] = df.apply(
                        lambda row: not row['price_including_tax'] > 0,
                        axis=1
                        )
        corrupt_tax_df = df[df['no_tax'] == True]
        err_dict['no_tax'] = corrupt_tax_df.shape[0]
    else:
        df['no_tax'] = False
        err_dict['no_tax'] = -1
    if 'float' in str(df['price_excluding_tax'].dtypes):
        df['no_taxfree'] = df.apply(
                        lambda row: not row['price_excluding_tax'] > 0,
                        axis=1
                        )
        corrupt_taxfree_df = df[df['no_taxfree'] == True]
        err_dict['no_taxfree'] = corrupt_taxfree_df.shape[0]
    else:
        df['no_taxfree'] = False
        err_dict['no_taxfree'] = -1
    if 'int' in str(df['number_available'].dtypes):
        df['unavailable'] = df.apply(
                        lambda row: not (row['number_available'] > 0),
                        axis=1
                        )
        unavailable_df = df[df['unavailable'] == True]
        err_dict['unavailable'] = unavailable_df.shape[0]
    else:
        df['unavailable'] = False
        err_dict['unavailable'] = -1
    if 'int' in str(df['review_rating'].dtypes):
        df['unrated'] = df.apply(
                        lambda row:
                         row['review_rating'] not in range(1,6)
                        , axis=1
                        )
        unrated_df = df[df['unrated'] == True]
        err_dict['unrated'] = unrated_df.shape[0]
    else:
        df['unrated'] = False
        err_dict['unrated'] = -1
    try:
        df['no_upc'] = df.apply(
            lambda row: len(row['universal_product_code']) != 16
            , axis=1
            )
        corrupt_upc_df = df[df['no_upc'] == True]
        err_dict['no_upc'] = corrupt_upc_df.shape[0]
    except Exception:
        df['no_upc'] = False
        err_dict['no_upc'] = -1
    try:
        df['no_description'] = df.apply(
            lambda row: len(row['product_description']) < 2
            , axis=1
            )
        description_df = df[df['no_description'] == True]
        err_dict['no_description'] = description_df.shape[0]
    except Exception:
        df['no_description'] = False
        err_dict['no_description'] = -1
    try:
        df['no_cover'] = df.apply(
            lambda r:
            img_path + r['image_url'].split('/')[-1] not in img_files
            , axis=1
            )
        no_cover_df = df[df['no_cover'] == True]
        err_dict['no_cover'] = no_cover_df.shape[0]
    except Exception:
        df['no_cover'] = False
        err_dict['no_cover'] = -1
    
    return (df, err_dict)

