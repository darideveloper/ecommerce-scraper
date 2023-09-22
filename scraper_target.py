import os
from dotenv import load_dotenv
from scraper import Scraper
from db import Database

# read .env file
load_dotenv ()
MAX_PRODUCTS = int(os.getenv ("MAX_PRODUCTS"))
CHROME_PATH = os.getenv ("CHROME_PATH")

class ScraperTarget (Scraper):
    
    def __init__ (self, keyword:str, db:Database):
        """ Start scraper for target

        Args:
            keyword (str): product to search
            db (Database): database instance
        """

        # Css self.selectors
        self.selectors = {
            'product': '.jZzlfv > .dOpyUp',
            'image': 'img',
            'title': 'div[title] > a',
            'rate_num': '[data-test="ratings"] > span',
            'reviews': '[data-test="rating-count"]',
            'sponsored': '[data-test="sponsoredText"]', 
            'best_seller': '',
            'price': '[data-test="current-price"] > span', 
            'sales': '',
            'link': 'div[title] > a',
            "search_bar": '',
            "search_btn": '',
        }
        
        self.store = "target"
        self.start_product = 1
     
        # Send data to scraper
        super().__init__ (keyword, db)
        
    def __load_page__ (self, product:str):
        """ Load target search page

        Args:
            product (str): product to search
        """
        
        product_clean = product.replace (" ", "+")
        link = f" https://www.target.com/s?searchTerm={product_clean}&facetedValue=5zktx&sortBy=bestselling"
        self.set_page (link)
        
    def __get_is_sponsored__ (self, text:str) -> str:
        """ Get if the product is sponsored in target

        Args:
            text (str): sponsored text

        Returns:
            bool: True if the product is sponsored
        """
        
        if text:
            return True
        else:
            return False
    
    def __get_clean_price__ (self, text:str) -> str:
        """ Get product clean price in aliexpress

        Args:
            text (str): price as text

        Returns:
            str: clean price
        """
        
        # $49.99 - $104.99
        price_parts = text.split (" ")
        price = price_parts[0].replace ("$", "").replace (",", "")
        
        if price.replace (".", "").isdigit ():
            return price
        else:
            return ""
    
    def get_product_link (self, selector:str) -> str:
        """ Get product link with selector, from href

        Args:
            selector (str): css selector

        Returns:
            str: product link in store
        """
        
        link = self.get_attrib (selector, "href")
        if not link.startswith ("https:"):
            link = "https://www.target.com" + link
        
        return link
    
    # def get_rate_num (self, selector:str) -> float:
    #     """ Get product rate number with selector

    #     Args:
    #         selector (str): css selector

    #     Returns:
    #         float: product rate as float
    #     """
        
    #     rate_num = self.get_text (selector)
        
    #     if rate_num:
    #         rate_num = float(rate_num.split (" ")[0])
    #     else:
    #         rate_num = 0.0
            
    #     return rate_num