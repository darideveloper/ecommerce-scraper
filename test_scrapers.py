import os
from db import Database
from dotenv import load_dotenv
from scraper_amazon import ScraperAmazon
from scraper_aliexpress import ScraperAliexpress
from scraper_ebay import ScraperEbay
from scraper_target import ScraperTarget
from scraper_walmart import ScraperWalmart

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

def start_scrapers (keyword:str):
    """ Start all scrapers

    Args:
        keyword (str): _description_
    """
    
    classes = [ScraperAmazon, ScraperAliexpress, ScraperEbay, ScraperTarget, ScraperWalmart]
    # classes = [ScraperEbay]
        
    for class_elem in classes:
        instance = class_elem(keyword, db)
        instance.get_results ()
        
start_scrapers ("protein")