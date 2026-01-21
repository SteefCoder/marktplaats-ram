from datetime import datetime, timedelta

from dotenv import find_dotenv, load_dotenv
import requests

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
assert CLIENT_ID is not None and CLIENT_SECRET is not None

# Sandbox endpoint
TOKEN_ENDPOINT = "https://auth.demo.qa-mp.so/accounts/oauth/token"



def oauth_get_token(code: str):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(TOKEN_ENDPOINT, json=data)
    response.raise_for_status()
    token_info = response.json()
    
    expires = datetime.now() + timedelta(seconds=token_info['expires_in'])

    return {
        'access_token': token_info['access_token'],
        'expires': expires.isoformat(),
        'refresh_token': token_info['refresh_token'],
        'scope': token_info['scope']
    }


def oauth_refresh_token():
    REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')
    assert REFRESH_TOKEN is not None

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(TOKEN_ENDPOINT, json=data)
    response.raise_for_status() 
    token_info = response.json()

    expires = datetime.now() + timedelta(seconds=token_info['expires_in'])


    return {
        'access_token': token_info['access_token'],
        'expires': expires.isoformat(),
        'refresh_token': token_info['refresh_token'],
        'scope': token_info['scope']
    }

