import os
from dotenv import load_dotenv
from scraper import Scraper
from db import Database

# read .env file
load_dotenv ()
MAX_PRODUCTS = int(os.getenv ("MAX_PRODUCTS"))
CHROME_PATH = os.getenv ("CHROME_PATH")

class ScraperAmazon (Scraper):
    
    def __init__ (self, keyword:str, db:Database):
        """ Start scraper for amazon

        Args:
            keyword (str): product to search
            db (Database): database instance
        """

        # Css self.selectors
        self.selectors = {
            'product': '[data-asin][data-uuid]',
            'image': 'img',
            'title': 'h2',
            'rate_num': 'span[aria-label]:nth-child(1)',
            'reviews': 'span[aria-label]:nth-child(2)',
            'sponsored': '[aria-label~="Sponsored"]',
            'best_seller': '.a-row.a-badge-region',
            'price': 'a.a-size-base .a-offscreen',
            'sales': '.a-row.a-size-base > span.a-color-secondary:only-child',
            'link': 'a',
            "search_bar": '',
            "search_btn": '',
        }
        
        self.store = "amazon"
        self.start_product = 6
        
        # Get proxy from pyproxy
        proxy_data = Scraper.proxy.get_proxy_webshare ()
        
        # Send data to scraper
        super().__init__ (
            keyword, 
            db, 
            proxy_data["proxy_address"], 
            proxy_data["port"]
        )
        
    def __load_page__ (self, product:str):
        """ Load amazon search page

        Args:
            product (str): product to search
        """
        
        link = f"https://www.amazon.com/s?k={product}&s=review-rank"
        self.set_page (link)

    def __get_is_sponsored__ (self, text:str) -> str:
        """ Get if the product is sponsored in amazon

        Args:
            text (str): sponsored text

        Returns:
            bool: True if the product is sponsored
        """
        
        return text != ""
    
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
    
    def get_product_link (self, selector:str) -> str:
        """ Get product link with selector, from href

        Args:
            selector (str): css selector

        Returns:
            str: product link in store
        """
        
        link = self.get_attrib (selector, "href")
        link = "https://www.amazon.com" + link
        return link