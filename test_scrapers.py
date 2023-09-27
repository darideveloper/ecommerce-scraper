import os
from threading import Thread
from db import Database
from dotenv import load_dotenv
from scraper import Scraper
from scraper_aliexpress import ScraperAliexpress
from scraper_amazon import ScraperAmazon
from scraper_ebay import ScraperEbay

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
    
    scraper = scraper_class (keyword, db)
    scraper.get_results ()

def start_scrapers (keyword:str):
    """ Start all scrapers

    Args:
        keyword (str): _description_
    """
    
    classes = [ScraperAliexpress, ScraperAmazon, ScraperEbay]
    
    for class_elem in classes:
        
        # Run functions with and without threads
        if USE_THREADING:
            thread_scraper = Thread (target=start_scraper, args=(class_elem, keyword))
            thread_scraper.start ()
        else:
            start_scraper (class_elem, keyword)
        
start_scrapers ("protein")