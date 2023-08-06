# Author: Samuel Lucidi <mansam@csh.rit.edu>

__version__ = "0.1.89"

import requests
import urllib
import ConfigParser
import liveconnect.conf
import liveconnect.exceptions
config = ConfigParser.SafeConfigParser()
config.read(liveconnect.conf.liveconnect_config_locations)

def connect():
	client_id = liveconnect.config.get('liveconnect', 'client_id')
	client_secret = liveconnect.config.get('liveconnect', 'client_secret')
	return LiveConnect(client_id, client_secret)

class LiveConnect(object):

	def __init__(self, client_id, client_secret):

		self.client_id = client_id
		self.client_secret = client_secret
		self.user_auth_url = 'https://login.live.com/oauth20_authorize.srf'
		self.token_auth_url = 'https://login.live.com/oauth20_token.srf'
		self.mobile_redirect = 'https://login.live.com/oauth20_desktop.srf'

	def authorize(self, refresh_token=None, auth_code=None, redirect_uri=None):
		"""
		Use a previously received auth code or refresh token to get a new
		access token and refresh token if applicable.

		"""

		if not redirect_uri:
			redirect_uri = self.mobile_redirect
		params = {
			"client_id":self.client_id, 
			"client_secret":self.client_secret,
			"redirect_uri":redirect_uri
		}
		if refresh_token:
			params["refresh_token"] = refresh_token
			params["grant_type"] = "refresh_token"
		elif auth_code:
			params["code"] = auth_code
			params["grant_type"] = "authorization_code"
		else:
			raise liveconnect.exceptions.AuthorizationError('Must specify an authorization code or a refresh token.')
		return requests.post(self.token_auth_url, params).json()	

	def generate_auth_url(self, scopes=['wl.basic'], redirect_uri=None):
		"""
		Generate a link that a user must visit to authorize the app
		to make requests in their name.

		"""

		if not redirect_uri:
			redirect_uri = self.mobile_redirect
		params = {
			"client_id":self.client_id, 
			"client_secret":self.client_secret,
			"scope":' '.join(scopes),
			"response_type":"code",
			"redirect_uri":redirect_uri
		}
		return "%s?%s" % (self.user_auth_url, urllib.urlencode(params))