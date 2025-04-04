from io import StringIO
import requests
import json
import pandas as pd
import time
import os

from http.client import HTTPSConnection
from base64 import b64encode

from dotenv import load_dotenv

load_dotenv()


class COLORS_CLASS:
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"
COLORS = COLORS_CLASS()
    

def log(o, color: str = None):
    if isinstance(o, dict) or isinstance(o, list):
        if color == "red":
            print(f"\033[91m{json.dumps(o, indent=2)}\033[0m")
        elif color == "green":
            print(f"\033[92m{json.dumps(o, indent=2)}\033[0m")
        elif color == "yellow":
            print(f"\033[93m{json.dumps(o, indent=2)}\033[0m")
        elif color == "blue":
            print(f"\033[94m{json.dumps(o, indent=2)}\033[0m")
        else:
            print(json.dumps(o, indent=2))
    
    else:
        if color == "red":
            print(f"\033[91m{o}\033[0m")
        elif color == "green":
            print(f"\033[92m{o}\033[0m")
        elif color == "yellow":
            print(f"\033[93m{o}\033[0m")
        elif color == "blue":
            print(f"\033[94m{o}\033[0m")
        else:
            print(o)

def get_results(response):
    return response.get("results", [])

def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'

class CollibraAPI:
    token: str = None
    session: requests.Session = None
    STANDARD_HEADERS = { "Content-Type": "application/json"  }

    def __init__(self):
        self.COLLIBRA_URL = os.getenv('COLLIBRA_URL')
        self.BASE_URL = f"{self.COLLIBRA_URL}/rest/2.0"
        self.username = os.getenv('COLLIBRA_USERNAME')
        self.password = os.getenv('COLLIBRA_PASSWORD')
        self.login()

   
    def login(self):
        url = f"{self.BASE_URL}/auth/sessions"
        payload = {
            "username": self.username,
            "password": self.password,
        }
        

        self.session = requests.Session()
        response = self.session.post(url, headers=CollibraAPI.STANDARD_HEADERS, json=payload)
        # print(response.json())
        if response.status_code == 200:
            csfrToken = response.json().get("csrfToken")
            # Store the session ID for future API requests
            CollibraAPI.STANDARD_HEADERS["X-CSRF-TOKEN"] = csfrToken
            self.token = csfrToken
            return csfrToken
        else:
            raise Exception("Failed to login to Collibra API")


    def call(self, url_path: str, json: dict = None, parameters: dict = None, method: str = "get", result_type = "json"):
        url = f"{self.BASE_URL}/{url_path}"

        # Convert parameters from dict to url
        if parameters:
            url += "?"
            url += "&".join([f"{key}={value}" for key, value in parameters.items()])

        #print(f"Calling {method} {url}")
        #print(json, parameters)
        #print(self.session.headers, self.session.auth, self.session.cookies)
        response = self.session.request(method=method, url=url, headers=CollibraAPI.STANDARD_HEADERS, json=json)
        
        if response.status_code > 299 :
            log(response.status_code, COLORS.RED)
            log(response.text, COLORS.RED)
            return None
        #log("OK")
        if result_type == "json":
            return response.json()
        else:
            return response
    
