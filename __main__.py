import os
from threading import Thread
from scraper_amazon import ScraperAmazon
from scraper_aliexpress import ScraperAliexpress
from dotenv import load_dotenv

load_dotenv ()
THREADING = os.getenv ("THREADING") == "True"

REFERRAL_LINK = ""
KEYWORD = "ssd 2tb"

classes = [ScraperAmazon, ScraperAliexpress]

# Create instances
instances = []
for class_elem in classes:
    instance = class_elem(KEYWORD, REFERRAL_LINK)
    instances.append (instance)
    
# Start threads
for instance in instances:    
    if THREADING:
        thread_obj = Thread(target=instance.get_results)
        thread_obj.start ()
    else:
        instance.get_results ()
        