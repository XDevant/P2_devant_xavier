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
        String: file path
    Add booléan rows to df after checking data.
    Build repport as error dict.
    Return: 
        (Panda Dataframe, Dict); the input df and an error dict
    """
    err_dict = {}

    try:
        df['no_tax'] = df.apply(
                        lambda row: not row['price_including_tax'] > 0,
                        axis=1
                        )
        err_dict['no_tax'] = df[df['no_tax'] == True].shape[0]
    except Exception:
        df['no_tax'] = False
        err_dict['no_tax'] = -1

    try:
        df['no_taxfree'] = df.apply(
                        lambda row: not row['price_excluding_tax'] > 0,
                        axis=1
                        )
        err_dict['no_taxfree'] = df[df['no_taxfree'] == True].shape[0]
    except Exception:
        df['no_taxfree'] = False
        err_dict['no_taxfree'] = -1

    try:
        df['no_stock'] = df.apply(
                        lambda row: not (row['number_available'] > 0),
                        axis=1
                        )
        unavailable_df = df[df['no_stock'] == True]
        err_dict['no_stock'] = unavailable_df.shape[0]
    except Exception:
        df['no_stock'] = False
        err_dict['no_stock'] = -1

    try:
        df['no_rating'] = df.apply(
                        lambda row:
                         int(row['review_rating']) not in range(1,6)
                        , axis=1
                        )
        err_dict['no_rating'] = df[df['no_rating'] == True].shape[0]
    except Exception:
        df['no_rating'] = False
        err_dict['no_rating'] = -1

    try:
        df['no_upc'] = df.apply(
            lambda row: len(row['universal_product_code']) != 16
            , axis=1
            )
        err_dict['no_upc'] = df[df['no_upc'] == True].shape[0]
    except Exception:
        df['no_upc'] = False
        err_dict['no_upc'] = -1

    try:
        df['no_title'] = df.apply(
            lambda row: 
            row['product_page_url'].split('_')[0].split('/')[-1]
                .split('-')[0] != ''.join(''.join(''.join(''.join(
                    row['title'].split(' ')[0].lower().strip('(,:#.%')
                    .split('\'')).split(',')).split('/')).split(')'))
            , axis=1
            )
        err_dict['no_title'] = df[df['no_title'] == True].shape[0]
    except Exception:
        df['no_title'] = False
        err_dict['no_title'] = -1

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
        err_dict['no_cover'] = df[df['no_cover'] == True].shape[0]
    except Exception:
        df['no_cover'] = False
        err_dict['no_cover'] = -1
    
    return (df, err_dict)

