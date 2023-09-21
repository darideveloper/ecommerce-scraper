import os
from scraper_amazon import ScraperAmazon
from scraper_aliexpress import ScraperAliexpress
from scraper_ebay import ScraperEbay
from scraper_target import ScraperTarget
from scraper_walmart import ScraperWalmart
from dotenv import load_dotenv

load_dotenv ()
USE_THREADING = os.getenv ("USE_THREADING") == "True"

KEYWORD = "ssd"

classes = [ScraperAmazon, ScraperAliexpress, ScraperEbay, ScraperTarget, ScraperWalmart]
# classes = [ScraperEbay]
    
for class_elem in classes:
    instance = class_elem(KEYWORD)
    instance.get_results ()
    