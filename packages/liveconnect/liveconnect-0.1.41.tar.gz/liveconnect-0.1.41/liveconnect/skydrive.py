import liveconnect
import liveconnect.exceptions
import requests
import urllib


class SkyDrive(liveconnect.LiveConnect):

    def __init__(self, client_id, client_secret):
        liveconnect.LiveConnect.__init__(self, client_id, client_secret)

        self.api_url = "https://apis.live.net/v5.0/"
        self.default_scopes = ['wl.basic', 'wl.skydrive', 'wl.skydrive_update']

    def generate_auth_url(self, scopes=[], redirect_uri=None):
        if not scopes:
            scopes = self.default_scopes
        return liveconnect.LiveConnect.generate_auth_url(self,
                                                    scopes=scopes,
                                                    redirect_uri=redirect_uri)

    def _request(self, method, url, auth_token, refresh_token=None, query={},
                                                       auth_header=False, files=None):
        """
        Make a request to the SkyDrive api. Returns a dictionary containing
        the response from the SkyDrive api.

        """

        params = {
            "access_token": auth_token
        }
        for k in query:
            params[k] = query[k]
        headers = {}
        if auth_header:
            headers["Authorization"] = 'Bearer %s' % auth_token

        request_method = getattr(requests, method)
        encoded_parameters = urllib.urlencode(params)
        url = "%s%s?%s" % (self.api_url, url, encoded_parameters)
        response = request_method(url, headers=headers, files=files)
        if response.status_code == 200:  # OK
            return response.json()
        else:
            response.raise_for_status()

    def get_quota(self, auth_token=None, refresh_token=None):
        return self._request('get', 'me/skydrive/quota', auth_token, refresh_token=refresh_token)

    def get(self, file_id="", auth_token=None, refresh_token=None):
        return self._request('get', 'me/skydrive/%s/content' % file_id,
                                auth_token,
                                refresh_token=refresh_token,
                                query={"download": 'true'},
                                raw=True)

    def list_dir(self, folder='me/skydrive', auth_token=None, refresh_token=None):
        return self._request('get', '%s/files' % folder, auth_token, refresh_token=refresh_token)

    def info(self, file_id="", auth_token=None, refresh_token=None):
        return self._request('get', file_id, auth_token)

    def put(self, name=None, fobj=None, folder_id="me/skydrive", auth_token=None, refresh_token=None, overwrite=True):
        """
        Upload a file to SkyDrive, by default overwriting any file that exists with the selected name.

        :param name: Name to create file as in SkyDrive.
        :type name: str

        :param fobj: File to upload
        :type fobj: File or File-like object

        :param folder_id: SkyDrive ID of folder to create file in
        :type folder_id: str

        :param auth_token: Access token of user to connect as
        :type auth_token: str

        :param refresh_token: Refresh token of user to connect as
        :type refresh_token: str

        :param overwrite: Overwrite existing file (default: True)
        :type overwrite: boolean

        :rtype: dictionary

        """

        return self._request('post', "%s/files" % folder_id, auth_token, files={"file":(name, fobj)})
