import json
import random
from datetime import datetime
from database.mysql import MySQL

class Database (MySQL):
    
    def __init__ (self, server:str, database:str, username:str, password:str):
        """ Connect with mysql db

        Args:
            server (str): server host
            database (str): database name
            username (str): database username
            password (str): database password
        """
        
        super().__init__(server, database, username, password)
        
        self.status = self.__get_status__ ()
        self.api_keys = self.__get_api_keys__ ()
        self.stores = self.get_stores ()
    
    def __get_status__ (self) -> dict:
        """ Retuen status from database as dictionary

        Returns:
            dict: status
            {
                "to do": 1,
                "working": 2,
                "done": 3
            }
        """
        
        query = "SELECT * FROM status"
        data = self.run_sql (query)
        
        status = {}
        for row in data:
            status[row["name"]] = row["id"]
            
        return status
    
    def __get_api_keys__ (self) -> dict:
        """ Retuen api keys from database as dictionary

        Returns:
            dict: status
            {
                "api-key-1": 1,
                "api-key-2": 2,
            }
        """
        
        query = "SELECT * FROM apikeys"
        data = self.run_sql (query)
        
        status = {}
        for row in data:
            status[row["api_key"]] = row["id"]
            
        return status
    
    def get_stores (self) -> dict:
        """ Query current stores in database 
        
        Returns:
            dict: stores (name and id)
            
            {
                "amazon": {
                    "id": 1,
                    "use_proxies": 1
                },
                "aliexpress": {
                    "id": 2,
                    "use_proxies": 1
                },
                "ebay": {
                    "id": 3,
                    "use_proxies": 0
                },
                ...
            }
        """
        
        print ("Getting stores from database")
        
        # Query all stores 
        query = "select * from stores"
        results = self.run_sql(query)
        
        data = {}
        for row in results:
            data[row["name"]] = {
                "id": row["id"],
                "use_proxies": row["use_proxies"]
            }
        
        return data
    
    def save_products (self, products_data:list):
        """ Save products in database

        Args:
            products_data (list): list of dict with products data
        """
        
        print (f"Saving {len(products_data)} products in database")
        
        for product in products_data:
            
            # Get product data
            image = product["image"]
            title = product["title"]
            rate_num = product["rate_num"]
            reviews = product["reviews"]
            price = product["price"]
            best_seller = 1 if product["best_seller"] else 0          
            sales = product["sales"]
            link = product["link"]
            id_store = product["id_store"]
            id_request = product["id_request"]
            
            # Generate sql query
            query = f"""
                INSERT INTO products (
                    image, 
                    title, 
                    rate_num, 
                    reviews, 
                    price, 
                    best_seller, 
                    sales, 
                    link, 
                    id_store,
                    id_request
                ) VALUES (
                    '{image}', 
                    '{title}', 
                    {rate_num}, 
                    {reviews}, 
                    {price}, 
                    {best_seller}, 
                    {sales}, 
                    '{link}',
                    {id_store},
                    {id_request}
                ); 
            """.replace ("\n", "")
                            
            # Save data
            self.run_sql(query)
            
    def delete_products (self):
        """ Delete all rows from products table """
        
        print ("Deleting all products from database")
        
        query = "delete from products"
        self.run_sql(query)
        
    def validate_token (self, token:str):
        """ Validate if token exist in database and is active

        Args:
            token (str): api access token
        """
        
        token_cencured = token[:5] + "..."
        print (f"Validating token {token_cencured}")
        
        token = self.get_clean_text (token)
        
        query = f"""
            SELECT id 
            FROM apikeys 
            WHERE 
                api_key = '{token}'
                AND
                is_active = 1
        """
        
        api_key_found = self.run_sql (query)
        
        if api_key_found:
            return True
        else:
            return False
                
    def create_new_request (self, api_key:str) -> int:
        """  Save a new request in database with status "to do" 
        
        Args:
            api_key (str): api access token
            
        Returns:
            int: id of new request
        """
        
        print ("Creating new request in database")
        
        # Get status for new requests
        status_todo_id = self.status["to do"]
        
        # Get api key id
        api_key_id = self.api_keys[api_key] 
        
        # get and fomat current datetime
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save new request
        query = f"""
            INSERT INTO requests (status, todo_datetime, api_key) 
            VALUES ({status_todo_id}, '{current_datetime}', {api_key_id})
        """
        self.run_sql (query)
        
        # Query id of new request
        query = f"""
            SELECT id 
            FROM requests
            WHERE
                status = {status_todo_id}
                AND
                api_key = {api_key_id}
                AND
                todo_datetime = '{current_datetime}'
        """
        id = self.run_sql (query)[0]["id"]
        return id
    
    def update_request_status (self, request_id:int, status_name:str):
        """ Update request status in db
        
        Args:
            request_id (int): request id
            status_name (str): status name
        """
        
        print (f"Request {request_id} status updated to {status_name}")
        
        status_num = self.status[status_name]
        
        query = f"""
            UPDATE requests
            SET status = {status_num}
            WHERE id = {request_id}
        """
        self.run_sql (query)
    
    def get_request_status (self, request_id:int) -> str:
        """ Get request status in db
        
        Args:
            request_id (int): request id
            
        Returns:
            str: status name
        """
        
        query = f""" 
            SELECT status
            FROM requests
            WHERE id = {request_id}
        """
        
        status_results = self.run_sql (query)
        
        if not status_results:
            return ""
        
        status_num = status_results[0]["status"]
        for status_name, status_id in self.status.items ():
            if status_id == status_num:
                return status_name
            
        return ""
    
    def get_cookies_random (self, store_name:str) -> list:
        """ Get cookies from a random user in db

        Args:
            store_name (str): store name like amazon, ebay, etc

        Returns:
            list: list of dict with cookies (key and value)
        """
        
        print (f"Getting cookies from {store_name} store")
        
        # Get cookies from all users in the store
        id_store = self.stores[store_name]["id"]
        id_status = self.status["cookie on"]
        
        query = f"""
            SELECT cookies
            FROM cookies
            WHERE 
                id_store = {id_store}
                AND
                status = {id_status}
        """
        cookies_users = self.run_sql (query)
        
        if not cookies_users:
            return []
        
        # Select random user
        random_cookies_json = random.choice (cookies_users)["cookies"]
        random_cookies = json.loads (random_cookies_json)
        
        # Keep only cookie name and cookie value
        cookies_clean = []
        for cookie in random_cookies:
            cookies_clean.append ({
                "name": cookie["name"],
                "value": cookie["value"]
            })
        
        return cookies_clean