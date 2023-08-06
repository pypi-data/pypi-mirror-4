# -*- coding: utf-8 -*-

from eve import Eve
from eve.io.mongo import Validator
from eve.auth import BasicAuth, TokenAuth, HMACAuth
from hashlib import sha1
import hmac
from flask import request


class Auth(BasicAuth):
    def check_auth(self, username, password, allowed_roles):
        return username == 'admin' and password == 'secret'


class Validator(Validator):
    def _validate_cin(self, cin, field, value):
        if cin:
            pass

app = Eve(validator=Validator)

@app.before_request
def br():
    try:
        print "br"
        print request
    except:
        pass

@app.after_request
def ar(arg):
    try:
        print "ar"
        print arg
    except:
        pass
    return arg


if __name__ == '__main__':
    #app.events.on_getting += pre
    #app.events.on_get += post
    app.run(debug=True)
