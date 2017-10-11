import json
import os

import asana
from asana.session import AsanaOAuth2Session

from secrets import CLIENT_ID, CLIENT_SECRET

class Auth:
    def __init__(self):
        try:
            f = open(".oauth", "r")
            token = json.loads(f.readline())
            f.close()
            self.client = asana.Client.oauth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                token=token,
                token_updater=self.saveToken,
                auto_refresh_url=AsanaOAuth2Session.token_url,
                auto_refresh_kwargs={
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET
                },
            )
        except IOError:
            self.getToken()

    def saveToken(self, token):
        f = open('.oauth', 'w')
        f.write(json.dumps(token))
        f.close()
        os.chmod('.oauth', 0o600)

    def getToken(self):
        self.client = asana.Client.oauth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob',
            token_updater=self.saveToken,
            auto_refresh_url=AsanaOAuth2Session.token_url,
            auto_refresh_kwargs={
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            },
        )
        (url, state) = self.client.session.authorization_url()
        print("Go to the following link and enter the code:")
        print(url)
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass

        code = sys.stdin.readline().strip()
        token = self.client.session.fetch_token(code=code)
        self.saveToken(token)

    def getClient(self):
        return self.client
