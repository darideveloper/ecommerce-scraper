import os
import random
from dotenv import load_dotenv
import requests

load_dotenv ()
WEBSHARE_TOKEN = os.getenv ("WEBSHARE_TOKEN")

class Proxy (): 
    
    def __init__ (self):
        """ Auto load proxies from webshare """
        
        # self.proxies_webshare = self.__load_proxies_webshare__ ()
        pass
        
    def __load_proxies_webshare__ (self) -> list:
        """ Save webshare USA proxies, as class variable 
        
        Returns:
            list: list of proxies
            
            [
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
                },
                ...
            ]
        """
        
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
        return list(filter(lambda proxy: proxy["country_code"] == "US", proxies))
                
    def get_proxy_webshare (self) -> dict:
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
        
        return random.choice (self.proxies_webshare)
    
    def get_proxy_pyproxy (self) -> dict:
        """ Get proxy from pyproxy

        Returns:
            dict: proxy data
            {
                "proxy_address": str,
                "port": int
            }
        """
        
        res = requests.get ("https://acq.iemoapi.com/getProxyIp?protocol=http&num=1&regions=us&lb=1&return_type=txt")
        proxy = res.text.split (":")
        
        host = proxy[0]
        port = proxy[1].replace ("\r\n", "").replace(',"success"', "")
        
        return {
            "proxy_address": host,
            "port": int(port)
        }
        
    def get_proxy_iproyal (self) -> dict:
        """ Get proxy from iproyal

        Returns:
            dict: proxy data
            {
                "proxy_address": str,
                "port": int
            }
        """
        
        return {
            "proxy_address": "geo.iproyal.com",
            "port": 12321
        }
        
    def get_proxy_brightdata (self) -> dict:
        """ Get proxy from brightdata

        Returns:
            dict: proxy data
            {
                "proxy_address": str,
                "port": int
            }
        """
        
        return {
            "proxy_address": "brd.superproxy.io",
            "port": 22225,
        }