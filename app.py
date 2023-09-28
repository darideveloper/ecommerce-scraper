import os
import random
from time import sleep
from threading import Thread
from db import Database
from flask import Flask, request
from dotenv import load_dotenv
from scraper import Scraper
from scraper_amazon import ScraperAmazon
from scraper_aliexpress import ScraperAliexpress
from scraper_ebay import ScraperEbay

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
    """ Start an specific scraper and extract data

    Args:
        scraper_class (Scraper): Scraper class
        keyword (str): keyword to search
    """
    
    print (scraper_class)
    print (keyword)
    
    scraper = scraper_class (keyword, db)
    scraper.get_results ()
    
    # random_wait_time = random.randint (15, 30)
    # sleep (random_wait_time)

def start_scrapers (keyword:str, request_id:int):
    """ Start all scrapers

    Args:
        keyword (str): keyword to search
        request_id (int): request id
    """
    
    classes = [ScraperAliexpress]
    
    # Update request status to working
    db.update_request_status (request_id, "working")
    
    # Start scraping threads
    threads = []
    for class_elem in classes:
        
        # Run functions with and without threads
        if USE_THREADING:
            thread_scraper = Thread (target=start_scraper, args=(class_elem, keyword))
            thread_scraper.start ()
            threads.append (thread_scraper)
        else:
            start_scraper (class_elem, keyword)
            
    sleep (10)
            
    # Wait for all threads to finish
    while True:
        
        alive_threads = list (filter (lambda thread: thread.is_alive (), threads))
        if not alive_threads:
            break
        
        else:
            sleep (2)
            
    # Update request status to done
    db.update_request_status (request_id, "done")
    
@app.post ('/keyword/')
def keyword ():
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
    thread_scrapers = Thread (target=start_scrapers, args=(keyword, request_id))
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