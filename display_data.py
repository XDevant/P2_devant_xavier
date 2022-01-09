

def plural(number, text=''):
    if number**2 >= 4:
        if text == '':
            return 's'
        return text
    return ''


def print_note(counted, saved, expected, url):
    print(f"\n      ** Note: **")
    if saved >= 0:
        print(f"{saved} row{plural(saved)} detected and reported, expected {expected}")
    else:
        if counted >= 0:
            print(f"{counted} row{plural(counted)} detected but not reported, expected {expected}")
        else:
            print(f"(Unable to count errors and create report, expected {expected}")
    print(f"(2 description are missing on {url})")


def print_result(result, expected={}):

    for key, value in result.items():
        words = key.split('_')
        words = [word.capitalize() for word in words]
        key2 = ' '.join(words) + plural(value)
        if expected == {}:
            value_check = value != 0
            if 'error' not in key or value_check:
                print(f"{key2}: {value}")
        else:
            value_check = value != 0 or expected[key] != 0
            if 'error' not in key or value_check:
                print(f"{key2}: {value} (expected : {expected[key]})")


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

    name = file.split('/')[-1]
    for key, value in err_dict.items():
        key2 = ' '.join(key.split('-'))
        if value == -1:
            print(f"Unable to parse books with {key2} in {name}")
            parsing_errors += 1
        if value > 0:
            total_errors += value
            print(f"{value} book{plural(value)} with {key2} in {name}")
    return (total_errors, parsing_errors)