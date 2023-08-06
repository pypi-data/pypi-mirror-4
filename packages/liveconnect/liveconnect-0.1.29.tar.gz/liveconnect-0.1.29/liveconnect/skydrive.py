import liveconnect
import liveconnect.exceptions
import requests
import urllib


class SkyDrive(liveconnect.LiveConnect):

    def __init__(self, client_id, client_secret):
        liveconnect.LiveConnect.__init__(self, client_id, client_secret)
        self.api_url = "https://apis.live.net/v5.0/"

    def generate_auth_url(self, scopes=['wl.basic',
                                        'wl.skydrive',
                                        'wl.skydrive_update'],
                                        redirect_uri=None):

        return liveconnect.LiveConnect.generate_auth_url(self,
                                                    scopes=scopes,
                                                    redirect_uri=redirect_uri)

    def _request(self, method, url, auth_token, refresh_token=None, query={},
                                                       auth_header=False):
        params = {
            "access_token": auth_token
        }
        headers = {}
        if auth_header:
            headers["Authorization"] = 'Bearer %s' % auth_token

        request_method = getattr(requests, method)
        encoded_parameters = urllib.urlencode(params)
        url = "%s%s?%s" % (self.api_url, url, encoded_parameters)
        response = request_method(url, headers=headers)
        if response.status_code == 200:  # OK
            return response.json()
        else:
            response.raise_for_status()

    def get_quota(self, auth_token, refresh_token):
        return self._request('get', 'me/skydrive/quota', auth_token, refresh_token)

    def get(self, auth_token, refresh_token, file_id):
        return self._request('get', 'me/skydrive/%s/content' % file_id,
                                auth_token,
                                refresh_token,
                                query={"download": 'true'},
                                raw=True)

    def listdir(self, auth_token, refresh_token, folder='me/skydrive'):
        return self._request('get', '%s/files' % folder, auth_token, refresh_token)
