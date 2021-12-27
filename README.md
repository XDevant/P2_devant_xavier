Scrap.py is designed to scrap data from http://books.toscrape.com/

The spimplest way to test it is to:
1. Clone the repository on your own computer.

2. Create a new virtual environment in the same folder as scrap.py:

        python -m venv env

3. Activate the virtual environment
    + unix: source env/bin/activate
    + windows: env/Scripts/activate.bat

4. Install the dependencies via the requirement.txt file

        pip install -r requirements.txt

5. Run scrap.py:

        python3 scrap.py

Note: Scrap.py will create the Books-to-scrape/CSV and Books-to-scrape/Img folders 
to store the data in your current working directory.
