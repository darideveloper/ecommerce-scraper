import os
import random
from time import sleep
from dotenv import load_dotenv
from scraping.web_scraping import WebScraping
from abc import ABC, abstractmethod
from db import Database
from proxy import Proxy

# read .env file
load_dotenv ()
MAX_PRODUCTS = int(os.getenv ("MAX_PRODUCTS"))
USE_DEBUG = os.getenv ("USE_DEBUG") == "True"

# paths
CURRENT_FOLDER = os.path.dirname(__file__)
    
class Scraper (WebScraping, ABC):
    
    # proxy = Proxy ()
    # proxy_data = proxy.get_proxy_brightdata ()
        
    def __init__ (self, keyword:str, db:Database):
        """ Start scraper

        Args:
            keyword (str): product to search
            db (Database): database instance
            proxy_server (str): proxy server address
            proxy_port (int): proxy port
        """
        
        # Child properties
        # self.selectors = dict
        # self.store = str
        # self.start_product = int
        
        # Scraper settings
        self.keyword = keyword    
        self.db = db
        self.stores = db.get_stores ()   
        
        if self.stores[self.store]["use_proxies"]:
        
            # Open chrome
            super().__init__ (
                # proxy_server= Scraper.proxy_data["proxy_address"],
                # proxy_port=Scraper.proxy_data["port"],
                # proxy_user="brd-customer-hl_917cca2a-zone-residential",
                # proxy_pass="2y7d2jth6qsb",
            )        
            
        else:
            super().__init__ ()
        
        # Delete products in debug mode
        if USE_DEBUG:
            self.db.delete_products ()
    
    @abstractmethod
    def __load_page__ (self, product:str):
        """ Abstract method to get the search link

        Args:
            product (str): product to search
        """
        pass
    
    @abstractmethod    
    def __get_is_sponsored__ (self, text:str) -> bool:
        """ Abstract method to get if the product is sponsored

        Args:
            text (str): sponsored text

        Returns:
            bool: True if the product is sponsored
        """
        pass
    
    @abstractmethod    
    def __get_clean_price__ (self, text:str) -> str:
        """ Abstract method to get product clean price

        Args:
            text (str): price as text

        Returns:
            str: clean price
        """
        pass
    
    def get_reviews (self, selector:str) -> str:
        """ Abstract method to get product reviews number as text
        
        Args:
            selector (str): css selector

        Returns:
            str: reviews number as text
        """
        
        reviews = self.get_text (selector)
        return reviews
    
    def clean_text (self, text:str, chars:list) -> str:
        """ Clean extra characters from text

        Args:
            text (str): original text
            chars (list): characters to remove

        Returns:
            str: cleaned text
        """
        
        for char in chars:
            text = text.replace (char, "")
            
        return text
    
    def get_product_link (self, selector:str) -> str:
        """ Get product link with selector, from href

        Args:
            selector (str): css selector

        Returns:
            str: product link in store
        """
        
        link = self.get_attrib (selector, "href")
        if not link.startswith ("https:"):
            link = "https:" + link
        
        return link
    
    def get_rate_num (self, selector:str) -> float:
        """ Get product rate number with selector

        Args:
            selector (str): css selector

        Returns:
            float: product rate as float
        """
        
        rate_num = self.get_text (selector)
        
        if rate_num:
            rate_num = float(rate_num.split (" ")[0])
        else:
            rate_num = 0.0
            
        return rate_num
    
    def get_best_seller (self, selector:str) -> bool:
        """ Get True if a product is a best seller

        Args:
            selector (str): css selector

        Returns:
            bool: True if the product is a best seller
        """
        
        if selector:
            best_seller = self.get_text (selector)
            if best_seller:
                return True
            
        return False
    
    def get_results (self, request_id:int) -> list:
        """ Get the results from the search link
        
        Args:
            request_id (int): request id

        Returns:
            list: list of products
            [
                {
                    "image": str, 
                    "title": str,
                    "rate_num": float,
                    "reviews": int,
                    "price": float,
                    "best_seller": bool,
                    "sales": int,
                    "link": str,
                }, 
                ...
            ]
        """
        
        product = self.keyword.lower ()
        
        print (f"({self.store} - {request_id}) Searching products...")

        # Open chrome and load results page
        self.__load_page__ (product)
        self.zoom (5)
        self.go_bottom ()
        self.refresh_selenium ()
        
        self.save_page ("temp.html")

        # get the results in the page
        results_num = len(self.get_elems (self.selectors['product']))

        # Validate if there are results
        if results_num > 0:

            current_index = self.start_product
            extracted_products = 0

            print (f"({self.store} - {request_id}) Extracting data...")

            products_data = []
            while True:
                
                # Generate css self.selectors
                selector_product = self.selectors["product"] + f":nth-child({current_index})"
                selector_image = f'{selector_product} {self.selectors["image"]}'
                selector_title = f'{selector_product} {self.selectors["title"]}'
                selector_rate_num = f'{selector_product} {self.selectors["rate_num"]}'
                selector_reviews = f'{selector_product} {self.selectors["reviews"]}'
                selector_sponsored = f'{selector_product} {self.selectors["sponsored"]}'
                
                if self.selectors["best_seller"]:
                    selector_best_seller = f'{selector_product} {self.selectors["best_seller"]}'
                else:
                    selector_best_seller = ""
                    
                selector_price = f'{selector_product} {self.selectors["price"]}'
                
                if self.selectors["sales"]:
                    selector_sales = f'{selector_product} {self.selectors["sales"]}'
                else:
                    selector_sales = ""
                selector_link = f'{selector_product} {self.selectors["link"]}'
                
                # Incress product counter
                current_index += 1
                
                # Validate if there are not more products in the page
                if current_index - self.start_product > results_num:
                    print (f"({self.store} - {request_id}) No more products")
                    break
                
                # Skip products without price
                price = self.get_text (selector_price)
                if not price:
                    continue
                
                # Skip sponsored products
                sponsored = self.get_text (selector_sponsored)
                sponsored = self.__get_is_sponsored__ (sponsored)
                if sponsored:
                    continue
                            
                # Extract text from self.selectors
                image = self.get_attrib (selector_image, "src")    
                title = self.get_text (selector_title)
                    
                if selector_sales:
                    sales = self.get_text (selector_sales)
                    sales = sales.split (" ")[0]
                else:
                    sales = 0
                
                # Custom extract data
                reviews = self.get_reviews (selector_reviews)
                link = self.get_product_link (selector_link)
                rate_num = self.get_rate_num (selector_rate_num)
                best_seller = self.get_best_seller (selector_best_seller)
                
                # Clean data 
                price = self.__get_clean_price__ (price)
                if not price:
                    continue
                price = float(price)
                
                title = self.clean_text (title, [",", "'", '"'])
                
                if not image.startswith ("https"):
                    image = "https:" + image
                
                if reviews:
                    reviews = self.clean_text (reviews, [",", " ", "+", "productratings", "productrating"])
                    reviews = int(reviews)
                else:
                    reviews = 0
                    
                if sales:
                    sales = self.clean_text (sales, ["(", ")", "+", ",", " ", "sold", "."])
                    
                    # Convert "K" numbers
                    if "k" in sales.lower():
                        number_sales = float(sales[:-1])
                        number_sales = number_sales * 1000
                        sales = int(number_sales)
                    else:
                        sales = int(sales)
                else:
                    sales = 0
                    
                # TODO: add referral link
                
                # Incress counter of extracted products
                extracted_products += 1
                
                # Save data
                products_data.append ({
                    "image": image, 
                    "title": title,
                    "rate_num": rate_num,
                    "reviews": reviews,
                    "price": price,
                    "best_seller": best_seller,
                    "sales": sales,
                    "link": link,
                    "id_store": self.stores[self.store]["id"],
                    "id_request": request_id
                })
                
                # End loop when extract al required products
                if extracted_products >= MAX_PRODUCTS: 
                    break
                            
            # Save products in db
            self.db.save_products (products_data)
            
            print (f"({self.store} - {request_id}) {extracted_products} products saved")
        else:
            print (f"({self.store} - {request_id}) No results found")
        
        self.close_tab ()
        quit ()
    