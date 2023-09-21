import os
from dotenv import load_dotenv
from scraper import Scraper

# read .env file
load_dotenv ()
MAX_PRODUCTS = int(os.getenv ("MAX_PRODUCTS"))
CHROME_PATH = os.getenv ("CHROME_PATH")

class ScraperEbay (Scraper):
    
    def __init__ (self, keyword:str):
        """ Start scraper for ebay

        Args:
            keyword (str): product to search
        """
        

        # Css self.selectors
        self.selectors = {
            'product': 'li.s-item',
            'image': 'img',
            'title': '.s-item__title',
            'rate_num': '.x-star-rating > span',
            'reviews': '.s-item__reviews-count > span:nth-child(1)',
            'sponsored': '.s-item__sep div',
            'best_seller': '.s-item__etrs-text',
            'price': '.s-item__price',
            'sales': '.s-item__quantitySold',
            'link': 'a',
        }
        
        self.store = "ebay"
        self.start_product = 2
        
        # Send data to scraper
        super().__init__ (keyword)
        
    def __get_search_link__ (self, product:str) -> str:
        """ Get the search link in ebay

        Args:
            product (str): product to search

        Returns:
            str: store search link
        """
        
        product_clean = product.replace (" ", "+")  
        return f"https://www.ebay.com/sch/i.html?_nkw={product_clean}&LH_BIN=1&rt=nc&LH_ItemCondition=1000&LH_BIN=1&_fcid=1"

    def __get_is_sponsored__ (self, text:str) -> str:
        """ Get if the product is sponsored in ebay

        Args:
            text (str): sponsored text

        Returns:
            bool: True if the product is sponsored
        """
        
        return False
    
    def __get_clean_price__ (self, text:str) -> str:
        """ Get product clean price in aliexpress

        Args:
            text (str): price as text

        Returns:
            str: clean price
        """
        
        price_parts = text.split (" ")
        price = price_parts[1].replace ("$", "").replace (",", "")
        
        if price.replace (".", "").isdigit ():
            return price
        else:
            return ""