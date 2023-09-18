import os
import random
from dotenv import load_dotenv
import requests

load_dotenv ()
WEBSHARE_TOKEN = os.getenv ("WEBSHARE_TOKEN")

class Proxy (): 
    
    def __init__ (self):
        """ Auto load proxies from webshare """
        
        self.proxies = []
        
        self.__load_proxies__ ()
        
    def __load_proxies__ (self):
        """ Save webshare USA proxies, as class variable """
        
        # Query tokens from webshare
        res = requests.get (
            "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100",
            headers = {
                "Authorization": f"Token {WEBSHARE_TOKEN}"
            }
        )
        res.raise_for_status ()
        
        # Get wproxies from json
        json_data = res.json ()
        proxies = json_data["results"]
        
        # Filter USA proxies
        self.proxies = list(filter(lambda proxy: proxy["country_code"] == "US", proxies))
        
        print ()
        
    def get_proxy (self) -> dict:
        """ Return a random proxy from webshare

        Returns:
            dict: proxy data
            {
                "id": str,
                "username": str,
                "password": str,
                "proxy_address": str,
                "port": int,
                "valid": bool,
                "last_verification": datetime (iso),
                "country_code": str,
                "city_name": str,
                "asn_name": str,
                "asn_number": int,
                "high_country_confidence": bool,
                "created_at": datetime (iso),
            }
        """
        
        return random.choice (self.proxies)