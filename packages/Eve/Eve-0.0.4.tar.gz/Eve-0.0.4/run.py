# -*- coding: utf-8 -*-

from eve import Eve
from eve.io.mongo import Validator
from eve.auth import BasicAuth


class Auth(BasicAuth):
    def check_auth(self, username, password, allowed_roles):
        auth = username == 'admin' and password == 'secret'
        print allowed_roles
        role = 'admin' in allowed_roles if allowed_roles else True
        return auth and role


class Validator(Validator):
    def _validate_cin(self, cin, field, value):
        if cin:
            pass


if __name__ == '__main__':
    app = Eve(validator=Validator, auth=Auth)
    app.run(debug=True)
