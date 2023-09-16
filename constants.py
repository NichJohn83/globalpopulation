import os

bearer_token = os.getenv('BEARER_TOKEN') 
consumer_key = os.getenv('CONSUMER_KEY') 
consumer_secret = os.getenv('CONSUMER_SECRET') 
access_token = os.getenv('ACCESS_TOKEN') 
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET') 
auth_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"

