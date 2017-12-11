import urwid

"""
Input box that accepts OAuth tokens
"""
class TokenEdit(urwid.Edit):
    def __init__(self):
        urwid.register_signal(TokenEdit, 'TokenEdit-changed')
        prompt = ('seondary', u'  Authorization Token: ')
        super(TokenEdit, self).__init__(prompt, '')

    def keypress(self, size, key):
        if key == 'enter':
            urwid.emit_signal(self, 'TokenEdit-changed', self.edit_text)
        else:
            return super(TokenEdit, self).keypress(size, key)

class AuthPrompt(object):
    def __init__(self, auth_url, callback):
        self.callback = callback
        token_input = TokenEdit()
        urwid.connect_signal(token_input, 'TokenEdit-changed', self.callback)

        self.frame = urwid.Filler(urwid.Padding(
            urwid.Pile([
                urwid.Text('Visit %s and paste the token below.\n' % auth_url),
                token_input,
            ]),
            align='center',
            width='pack',
            left=2,
            right=2
        ))

    def callback(self, token):
        self.callback(token)

    def component(self):
        return self.frame
