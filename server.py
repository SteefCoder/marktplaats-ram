from dotenv import find_dotenv, set_key
from flask import Flask, request

from oauth import oauth_get_token

dotenv_path = find_dotenv()

app = Flask(__name__)


@app.route('/oauth-redirect', methods=['GET'])
def oauth_redirect():
    code = request.args.get('code')

    token_info = oauth_get_token(code)

    set_key(dotenv_path, 'TOKEN', token_info['access_token']
    set_key(dotenv_path, 'TOKEN_EXPIRES', token_info['expires'])
    set_key(dotenv_path, 'REFRESH_TOKEN', token_info['refresh_token'])

    return {}

