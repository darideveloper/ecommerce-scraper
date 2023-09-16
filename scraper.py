import os
from time import sleep
from dotenv import load_dotenv
from chrome_dev.chrome_dev import ChromDevWrapper
from abc import ABC, abstractmethod
from db import Database

# read .env file
load_dotenv ()
MAX_PRODUCTS = int(os.getenv ("MAX_PRODUCTS"))
CHROME_PATH = os.getenv ("CHROME_PATH")
DB_HOST = os.getenv ("DB_HOST")
DB_USER = os.getenv ("DB_USER")
DB_PASSWORD = os.getenv ("DB_PASSWORD")
DB_NAME = os.getenv ("DB_NAME")

class Scraper (ChromDevWrapper, ABC):
    
    db = Database (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
    
    def __init__ (self, keyword:str, referral_link:str):
        """ Start scraper

        Args:
            keyword (str): product to search
            referral_link (str): platform referral link
        """
        
        # Scraper settings
        self.keyword = keyword
        self.referral_link = referral_link
        
        # Open chrome
        super().__init__ (chrome_path=CHROME_PATH, start_killing=False)        
        
        # DEBUG: delete products
        self.db.delete_products ()
        
        # get stores from db
        self.stores = self.db.get_stores ()
        
        # Validate required atributes
        if not self.stores:
            raise Exception ("No stores found")
        
        if not self.start_product:
            self.start_product = 1
    
    @abstractmethod
    def __get_search_link__ (self, product:str) -> str:
        """ Abstract method to get the search link

        Args:
            product (str): product to search

        Returns:
            str: store search link
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
    
    @abstractmethod    
    def __get_reviews__ (self, selector:str) -> str:
        """ Abstract method to get product reviews number as text
        
        Args:
            selector (str): css selector

        Returns:
            str: reviews number as text
        """
        pass
    
    def __clean_text__ (self, text:str, chars:list) -> str:
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
    
    def get_results (self) -> list:
        """ Get the results from the search link

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
        
        print (f"({self.store}) Searching products...")

        # Open chrome and load results page
        search_link = self.__get_search_link__ (product)
        self.set_page (search_link)
        self.set_zoom (0.2)
        self.go_down ()
        sleep (2)

        # get the results in the page
        results_num = self.count_elems (self.selectors['product'])

        # Validate if there are results
        if results_num == 0:
            print (f"({self.store}) No results found")
            return []

        current_index = self.start_product
        extracted_products = 0

        print (f"({self.store}) Extracting data...")

        products_data = []
        while True:
            
            # Generate css self.selectors
            selector_product = self.selectors["product"] + f":nth-child({current_index})"
            selector_image = f'{selector_product} {self.selectors["image"]}'
            selector_title = f'{selector_product} {self.selectors["title"]}'
            selector_rate_num = f'{selector_product} {self.selectors["rate_num"]}'
            selector_reviews = f'{selector_product} {self.selectors["reviews"]}'
            selector_sponsored = f'{selector_product} {self.selectors["sponsored"]}'
            selector_best_seller = f'{selector_product} {self.selectors["best_seller"]}'
            selector_price = f'{selector_product} {self.selectors["price"]}'
            selector_sales = f'{selector_product} {self.selectors["sales"]}'
            selector_link = f'{selector_product} {self.selectors["link"]}'
            
            # Incress product counter
            current_index += 1
            
            # Validate if there are not more products in the page
            if current_index - self.start_product > results_num:
                print (f"({self.store}) No more products")
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
            rate_num = self.get_text (selector_rate_num)
            best_seller = self.get_text (selector_best_seller)
            sales = self.get_text (selector_sales)
            
            # Custom extract data
            reviews = self.__get_reviews__ (selector_reviews)
            link = self.get_product_link (selector_link)
                            
            # Clean data 
            price = self.__get_clean_price__ (price)
            if not price:
                continue
            price = float(price)
            
            title = self.__clean_text__ (title, [",", "'", '"'])
            
            if not image.startswith ("https"):
                image = "https:" + image
            
            if rate_num:
                rate_num = float(rate_num[0:3])
            else:
                rate_num = 0.0
            
            if reviews:
                reviews = self.__clean_text__ (reviews, [",", " ", "+", "productratings"])
                reviews = int(reviews)
            else:
                reviews = 0
                
            if best_seller:
                best_seller = True
            else:
                best_seller = False
                
            if sales:
                sales = self.__clean_text__ (sales, ["(", ")", "+", ",", " ", "sold"])
                
                # Convert "K" numbers
                if "k" in sales.lower():
                    number_sales = float(sales[:-1])
                    number_sales = number_sales * 1000
                    sales = int(number_sales)
                else:
                    sales = int(sales)
            else:
                sales = 0
                
            # /Kingston-Renegade-Internal-SFYRDK-2000G/dp/B0BJL7MMNF/ref=sr_1_2?keywords=ssd&qid=1694888235&sr=8-2
                
                
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
                "id_store": self.stores[self.store]["id"]
            })
            
            # End loop when extract al required products
            if extracted_products >= MAX_PRODUCTS: 
                break
                
        print (f"({self.store}) {extracted_products} products extracted")
        
        # Save products in db
        Scraper.db.save_products (products_data)
        
        print (f"({self.store}) {extracted_products} products saved")