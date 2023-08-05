API_KEY = 'T8W3RZ2NVHSD2LANYCEJ'
API_SECRET = 'NWiXxMS5RJmiVTGK_A2IO7HGZ2Tmswbg64q9JRTO'
API_URL = 'https://sandbox-insightsapi.radian6.com/'

from luminoso_api.client import LuminosoClient
from luminoso_api.oauth_connector import OAuthConnector

auth = OAuthConnector(API_KEY, API_SECRET, API_URL)
client = LuminosoClient(auth, API_URL, trailing_slash=False)
