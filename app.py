import os
from threading import Thread
from db import Database
from flask import Flask, request
from dotenv import load_dotenv
from scraper import Scraper
from scraper_amazon import ScraperAmazon
from scraper_aliexpress import ScraperAliexpress
from scraper_ebay import ScraperEbay
from scraper_target import ScraperTarget
from scraper_walmart import ScraperWalmart

app = Flask(__name__)

# Load env variables
load_dotenv ()
DB_HOST = os.getenv ("DB_HOST")
DB_USER = os.getenv ("DB_USER")
DB_PASSWORD = os.getenv ("DB_PASSWORD")
DB_NAME = os.getenv ("DB_NAME")
USE_DEBUG = os.getenv ("USE_DEBUG") == "True"
USE_THREADING = os.getenv ("USE_THREADING") == "True"

# Connect with database
db = Database(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)

def start_scraper (scraper_class:Scraper, keyword:str):
    """ SStart an specific scraper and extract data

    Args:
        scraper_class (Scraper): Scraper class
        keyword (str): keyword to search
    """
    
    scraper = scraper_class (keyword, db)
    scraper.get_results ()

def start_scrapers (keyword:str):
    """ Start all scrapers

    Args:
        keyword (str): _description_
    """
    
    classes = [ScraperAliexpress, ScraperTarget, ScraperWalmart]
    
    for class_elem in classes:
        
        # Run functions with and without threads
        if USE_THREADING:
            thread_scraper = Thread (target=start_scraper, args=(class_elem, keyword))
            thread_scraper.start ()
        else:
            start_scraper (class_elem, keyword)
    
@app.post ('/results/')
def start_scraper ():
    """ Initilize scraper in background """
    
    # Get json data
    json_data = request.get_json ()
    keyword = json_data.get ("keyword", "")
    api_key = json_data.get ("api-key", "")
    
    # Validate required data
    if not (keyword and api_key):
        return ({
            "status": "error",
            "message": "Keyword and api-key are required",
            "data": {}
        }, 400)
    
    # Validate if token exist in db
    api_key_valid = db.validate_token (api_key)
    if not api_key_valid:
        return ({
            "status": "error",
            "message": "Invalid api-key",
            "data": {}
        }, 401)
    
    # save request in db
    request_id = db.create_new_request (api_key)
    
    # initialize web scraper in background
    thread_scrapers = Thread (target=start_scrapers, args=(keyword,))
    thread_scrapers.start ()
    
    return {
        "status": "success",
        "message": "Scraper started in background",
        "data": {
            "request-id": request_id
        }
    }


if __name__ == "__main__":
    app.run(debug=True)