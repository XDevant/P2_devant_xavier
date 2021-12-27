Scrap.py is designed to scrap data from http://books.toscrape.com/

The spimplest way to test it is to:
_ Clone the repository on your own computer.
_ Create a new virtual environment in the same folder as scrap.py:
    python -m venv env
_ Activate the virtual environment
    unix: source env/bin/activate
    windows: env/Scripts/activate.bat
_ Install the dependencies via the requirement.txt file
    pip install -r requirements.txt
_ Run scrap.py:
    python3 scrap.py

Note: Scrap.py will create the Books-to-scrape/CSV and Books-to-scrape/Img folders 
to store the data in your current working directory.
