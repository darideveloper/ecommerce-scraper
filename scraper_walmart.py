import os
from dotenv import load_dotenv
from scraper import Scraper
from db import Database

# read .env file
load_dotenv ()
MAX_PRODUCTS = int(os.getenv ("MAX_PRODUCTS"))
CHROME_PATH = os.getenv ("CHROME_PATH")

class ScraperWalmart (Scraper):
    
    def __init__ (self, keyword:str, db:Database):
        """ Start scraper for walmart

        Args:
            keyword (str): product to search
            db (Database): database instance
        """

        # Css self.selectors
        self.selectors = {
            'product': 'div.ph1',
            'image': 'img',
            'title': 'a > span',
            'rate_num': 'div.mt2 .w_iUH7',
            'reviews': 'div.mt2 span[aria-hidden]',
            'sponsored': '', 
            'best_seller': '.tag-leading-badge',
            'price': '[data-automation-id="product-price"] .w_iUH7', 
            'sales': '',
            'link': 'a',
            "search_bar": '',
            "search_btn": '',
        }
        
        self.store = "walmart"
        self.start_product = 1
        
        # Send data to scraper
        super().__init__ (keyword, db)
   
    def __load_page__ (self, product:str):
        """ Load walmart search page

        Args:
            product (str): product to search
        """
        
        product_clean = product.replace (" ", "+")
        link = f"https://www.walmart.com/search?country=US&q={product_clean}&sort=best_seller"
        self.set_page (link)

    def __get_is_sponsored__ (self, text:str) -> str:
        """ Get if the product is sponsored in walmart

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
        
        # current price $39.99
        price_parts = text.split (" ")
        price = price_parts[-1].replace ("$", "").replace (",", "")
        
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
            link = "https://www.walmart.com" + link
        
        return link
    
    def get_best_seller (self, selector:str) -> bool:
        """ Get True if a product is a best seller

        Args:
            selector (str): css selector

        Returns:
            bool: True if the product is a best seller
        """
        
        if selector:
            best_seller = self.get_text (selector)
            if best_seller and best_seller == "Best seller":
                return True
            
        return False
    
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