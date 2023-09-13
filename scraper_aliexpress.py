import os
from dotenv import load_dotenv
from scraper import Scraper

# read .env file
load_dotenv ()
MAX_PRODUCTS = int(os.getenv ("MAX_PRODUCTS"))
CHROME_PATH = os.getenv ("CHROME_PATH")

class ScraperAliexpress (Scraper):
    
    def __init__ (self, keyword:str, referral_link:str):
        """ Start scraper for aliexpress

        Args:
            keyword (str): product to search
            referral_link (str): platform referral link
        """
        
        # Send data to scraper
        super().__init__ (keyword, referral_link)

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
        }
        
        self.store = "aliexpress"
        self.start_product = 1
        
    def __get_search_link__ (self, product:str) -> str:
        """ Get the search link in aliexpress

        Args:
            product (str): product to search

        Returns:
            str: store search link
        """

        product_clean = product.replace (" ", "-")
        return f"https://www.aliexpress.com/w/wholesale-{product_clean}.html?g=y&trafficChannel=main&isMall=y&sortType=total_tranpro_desc&isFavorite=y"


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
        
        price = self.__clean_text__ (price, ["$", "US "])
        
    def __get_reviews__ (self, selector:str) -> str:
        """ Get product reviews number as text
        
        Args:
            selector (str): css selector

        Returns:
            str: reviews number as text
        """
        
        reviews = self.get_attrib (selector, "aria-label")
        return reviews