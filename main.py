#!/usr/bin/env python3

import json
import os

import asana
from asana.session import AsanaOAuth2Session
import urwid

import secrets
from ui.auth import AuthPrompt
from ui.palette import palette

class NotAuthedException(Exception):
    def __init__(self):
        super(NotAuthedException, self)

class CmdAsana(object):
    """The main urwid loop
    """
    loop = None

    """Try to get an Asana client using stored tokens

    Raises:
        NotAuthedException: the user has not authorized the app
    """
    def get_client(self):
        try:
            f = open('.oauth', 'r')
            auth_json = f.read()
            f.close()
            token = json.loads(auth_json)
            self.client = asana.Client.oauth(
                client_id=secrets.CLIENT_ID,
                client_secret=secrets.CLIENT_SECRET,
                token=token,
                token_updater=self.save_token,
                auto_refresh_url=AsanaOAuth2Session.token_url,
            )
        except IOError:
            raise NotAuthedException()

    def authorize(self):
        self.client = asana.Client.oauth(
            client_id=secrets.CLIENT_ID,
            client_secret=secrets.CLIENT_SECRET,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob',
            token_updater=self.save_token,
            auto_refresh_url=AsanaOAuth2Session.token_url,
        )
        (url, _) = self.client.session.authorization_url()
        auth = AuthPrompt(url, self.auth_callback)

        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass

        self.loop = urwid.MainLoop(
            auth.component(),
            unhandled_input=self.exit_handler,
            palette=palette
        )
        self.loop.run()

    def auth_callback(self, code):
        self.save_token(
            self.client.session.fetch_token(code=code))
        raise urwid.ExitMainLoop()


    def exit_handler(self, key):
        if key in ('q', 'Q', 'esc'):
            raise urwid.ExitMainLoop()

    def run(self):
        print("Running...", self.client.users.me())

    def save_token(self, token):
        f = open('.oauth', 'w')
        f.write(json.dumps(token))
        f.close()
        os.chmod('.oauth', 0o600)

def main():
    cmd_asana = CmdAsana()
    try:
        cmd_asana.get_client()
    except NotAuthedException:
        cmd_asana.authorize()

    cmd_asana.run()

if __name__ == "__main__":
    main()
