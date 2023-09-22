import os
from time import sleep
from dotenv import load_dotenv
from scraper import Scraper
from db import Database

# read .env file
load_dotenv ()
MAX_PRODUCTS = int(os.getenv ("MAX_PRODUCTS"))
CHROME_PATH = os.getenv ("CHROME_PATH")

class ScraperAliexpress (Scraper):
    
    def __init__ (self, keyword:str, db:Database):
        """ Start scraper for aliexpress

        Args:
            keyword (str): product to search
            db (Database): database instance
        """

        # Css self.selectors
        self.selectors = {
            'product': '#card-list > a',
            'image': 'img',
            'title': 'h1',
            'rate_num': '[class*="evaluation"]',
            'reviews': '[class*="evaluation"]',
            'sponsored': 'img + span',
            'best_seller': 'img[width="44.53125"]',
            'price': '[class*="price-sale"]',
            'sales': '[class*="trade-"]',
            'link': '',
            "search_bar": '#search-key',
            "search_btn": '.search-button',
        }
        
        self.store = "aliexpress"
        self.start_product = 1
        
        # Send data to scraper
        super().__init__ (keyword, db)
        
    def __load_page__ (self, product:str):
        """ Write a text in the search bar

        Args:
            product (str): product to search
        """
        
        self.set_page ("https://www.aliexpress.com/")
        sleep (1)
        self.send_data (self.selectors["search_bar"], product)
        sleep (1)
        self.click (self.selectors["search_btn"])
        sleep (1)
       
    def __get_is_sponsored__ (self, text:str) -> str:
        """ Get if the product is sponsored in aliexpress

        Args:
            text (str): sponsored text

        Returns:
            bool: True if the product is sponsored
        """

        return text.lower() == "ad"

    def __get_clean_price__ (self, text:str) -> str:
        """ Get product clean price in aliexpress

        Args:
            text (str): price as text

        Returns:
            str: clean price
        """
        
        price = self.clean_text (text, ["$", "US "])
        return price
        
    def get_reviews (self, selector:str) -> str:
        """ Get product reviews number as text
        
        Args:
            selector (str): css selector

        Returns:
            str: reviews number as text
        """
        
        reviews = self.get_attrib (selector, "aria-label")
        return reviews