import os
from flask import Flask, request
from db import Database
from dotenv import load_dotenv

app = Flask(__name__)

# Load env variables
load_dotenv ()
DB_HOST = os.getenv ("DB_HOST")
DB_USER = os.getenv ("DB_USER")
DB_PASSWORD = os.getenv ("DB_PASSWORD")
DB_NAME = os.getenv ("DB_NAME")
USE_DEBUG = os.getenv ("USE_DEBUG") == "True"

# Connect with database
db = Database(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)

@app.post ('/keyword/')
def start_scraper ():
    """ Initilize scraper in background """
    
    # Get json data
    json_data = request.get_json ()
    keyword = json_data.get ("keyword", "")
    api_key = json_data.get ("api-key", "")
    
    # Validate required data
    if not (keyword and api_key):
        return ({
            "status": "error",
            "message": "Keyword and api-key are required",
            "data": []
        }, 400)
    
    # Validate if token exist in db
    api_key_valid = db.validate_token (api_key)
    if not api_key_valid:
        return ({
            "status": "error",
            "message": "Invalid api-key",
            "data": []
        }, 401)
    
    # TODO: save request in db
    
    # TODO: initialize web scraper in background
    
    return {
        "status": "success",
        "message": "Scraper started in background",
        "data": []
    }


if __name__ == "__main__":
    app.run(debug=True)