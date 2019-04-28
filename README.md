# cmdasana
A curses CLI for Asana, using the Asana API.

## Requirments
* python 3
* [python-asana](https://github.com/Asana/python-asana)
* [urwid](http://urwid.org)
* [python-dateutil](https://github.com/dateutil/dateutil/)

## Setup
### Create an Asana OAuth app
See [instructions from Asana](https://asana.com/developers/documentation/getting-started/auth#register-an-app)
on how to create a new app. Use `urn:ietf:wg:oauth:2.0:oob` as the redirect
URL.

Once you create your app, save your client ID and secret in a file `secrets.py`:
```python
CLIENT_ID='...'
CLIENT_SECRET='...'
```

### Install dependencies
Using `pip`:
```
pip3 install asana urwid python-dateutil
```

## Usage
```
./main.py
```

When you first cmdasana, you will need to authorize the app in your browser.
Copy and paste your OAuth key into the terminal to get started.

## Navigation
Use arrow keys to navigate, `<enter>` to "click", and `<backspace>` to return to
the previous page.
