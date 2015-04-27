import webbrowser
# Credentials you get from adding a new consumer in twitter -> manage account
# -> integrated applications.
client_key="lNPmHMmEPYajuMltc2KuJuzMv"
client_secret = "B21Nh5x4yFbjesT47nsR1wJX4puMwmuNWQAMARw0sAWYeIEqc6"

# OAuth endpoints given in the Bitbucket API documentation
request_token_url = 'https://api.twitter.com/oauth/request_token'
callback_uri = 'http://omarashour.com'
base_authorization_url = 'https://api.twitter.com/oauth/authorize'
access_token_url = 'https://api.twitter.com/oauth/access_token'
protected_url = 'https://api.twitter.com/1.1/account/settings.json'

# 2. Fetch a request token
from requests_oauthlib import OAuth1Session
twitter = OAuth1Session(client_key, client_secret=client_secret,
        callback_uri=callback_uri)
twitter.fetch_request_token(request_token_url)

# 3. Redirect user to Bitbucket for authorization
authorization_url = twitter.authorization_url(base_authorization_url)
webbrowser.open_new_tab(authorization_url)
#print('Please go here and authorize,', authorization_url)

# 4. Get the authorization verifier code from the callback url
redirect_response = input('Paste the full redirect URL here: ')
twitter.parse_authorization_response(redirect_response)

# 5. Fetch the access token
twitter.fetch_access_token(access_token_url)

# 6. Fetch a protected resource, i.e. user profile
r = twitter.get(protected_url)
print(r.content)
