import os
from threading import Thread
from scraper_amazon import ScraperAmazon
from scraper_aliexpress import ScraperAliexpress
from scraper_ebay import ScraperEbay
from scraper_target import ScraperTarget
from dotenv import load_dotenv

load_dotenv ()
USE_THREADING = os.getenv ("USE_THREADING") == "True"

KEYWORD = "ssd"

classes = [ScraperAmazon, ScraperAliexpress, ScraperEbay, ScraperTarget]
# classes = [ScraperTarget]

# Create instances
instances = []
for class_elem in classes:
    instance = class_elem(KEYWORD)
    instances.append (instance)
    
# Start threads
for instance in instances:    
    if USE_THREADING:
        thread_obj = Thread(target=instance.get_results)
        thread_obj.start ()
    else:
        instance.get_results ()
        