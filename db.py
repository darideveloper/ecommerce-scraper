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
            
            # Generate sql query
            query = f"""INSERT INTO products (image, title, rate_num, reviews, price, best_seller, sales, link, id_store) 
            VALUES ('{image}', '{title}', {rate_num}, {reviews}, {price}, {best_seller}, {sales}, '{link}', {id_store}); """.replace ("\n", "")
                            
            # Save data
            self.run_sql(query)
            
    def delete_products (self):
        """ Delete all rows from products table """
        
        query = "delete from products"
        self.run_sql(query)