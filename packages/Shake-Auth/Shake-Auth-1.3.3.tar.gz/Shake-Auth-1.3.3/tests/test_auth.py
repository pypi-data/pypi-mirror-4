# -*- coding: utf-8 -*-
"""
"""
import os
from datetime import datetime

import pytest
import shake_auth
from shake import Shake, Request, local
from solution import SQLAlchemy
from werkzeug.test import EnvironBuilder


app_settings = {
    'SECRET_KEY': 'ee6864874322ff97d0f7380e815ff0a02493783c',
}

auth_settings = {
    'pepper': 'dc47d3062962d5b9f5828dccc47b9d7eda95ecf6',
}


def get_user_model():
    db = SQLAlchemy()

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        login = db.Column(db.Unicode(64),
            unique=True, nullable=False)
        email = db.Column(db.String(64),
            nullable=True)
        password = db.Column(db.String(140), nullable=True)
        date_joined = db.Column(db.DateTime, default=datetime.utcnow,
            nullable=False)
        last_sign_in = db.Column(db.DateTime,
            nullable=True)
        status = db.Column(db.String(1),
            default='A', nullable=False)
        
        def __init__(self, login, password=None, email=None):
            self.login = login
            self.password = password
            self.email = email
        
        def __repr__(self):
            if self.email:
                return '<User %s (%s)>' % (self.login, self.email)
            return '<User %s>' % self.login
    
    db.create_all()
    return User


def get_auth(hash_alg='sha512', hash_cost=10):
    User = get_user_model()
    settings = auth_settings.copy()
    settings['hash_alg'] = hash_alg
    settings['hash_cost'] = hash_cost
    settings['pepper'] = 'dc47d3062962d5b9f5828dccc47b9d7eda95ecf6'
    return shake_auth.Auth(User, **settings)


def test_settings():
    pepper = 'dc47d3062962d5b9f5828dccc47b9d7eda95ecf6'
    User = get_user_model()

    with pytest.raises(AssertionError):
        shake_auth.Auth(User)
    with pytest.raises(AssertionError):
        shake_auth.Auth(User, pepper=pepper, hash_alg='md5')
    with pytest.raises(AssertionError):
        shake_auth.Auth(User, pepper=pepper, hash_cost=-1)
    with pytest.raises(AssertionError):
        shake_auth.Auth(User, pepper=pepper, reset_expire=-1)


def test_create_user():
    auth = get_auth()
    user = auth.create_user(u'admin', u'passw')
    assert user.login == u'admin'
    alg, cost, salt, hashed = user.password.split('$')
    assert alg == 'dsha512'
    assert int(cost) == auth.settings['hash_cost']


def test_sign_in_out():
    app = Shake(__file__, app_settings)
    auth = get_auth()
    auth.init_app(app)
    user = auth.create_user(u'admin', u'passw')
    environ = get_test_env()
    request = app.make_request(environ)

    auth.sign_in(request, user)
    assert request.user.login
    
    auth.sign_out(request)
    assert request.user is None


def test_authenticate_by_password():
    auth = get_auth()
    credentials = {
        'login': u'admin',
        'password': u'passw',
    }
    user = auth.create_user(credentials['login'], credentials['password'])
    auser = auth.authenticate(credentials)

    assert auser
    assert user == auser
    assert not auth.authenticate({'login': credentials['login']})
    assert not auth.authenticate({'password': credentials['password']})

    bad = credentials.copy()
    bad['login'] = 'meh'
    assert not auth.authenticate(bad)

    bad = credentials.copy()
    bad['password'] = 'meh'
    assert not auth.authenticate(bad)


def test_authenticate_by_token():
    auth = get_auth()
    app = Shake(__file__, app_settings)
    auth.init_app(app)

    user = auth.create_user(u'admin', u'passw')
    token = auth.get_reset_token(user)

    auser = auth.authenticate({'token': str(token)})

    assert auser
    assert user == auser
    assert not auth.authenticate({})
    assert not auth.authenticate({'token': u'lalala'})


def test_authenticate_and_update():
    User = get_user_model()

    settings = auth_settings.copy()
    settings['hash_alg'] = 'sha512'
    settings['hash_cost'] = 10
    settings['pepper'] = 'dc47d3062962d5b9f5828dccc47b9d7eda95ecf6'
    auth = shake_auth.Auth(User, **settings)

    settings = settings.copy()
    settings['hash_alg'] = 'bcrypt'
    auth2 = shake_auth.Auth(User, **settings)

    credentials = {
        'login': u'admin',
        'password': u'passw',
    }
    user = auth.create_user(credentials['login'], credentials['password'])
    oldlogin = user.login
    oldpassw = user.password
    auser = auth2.authenticate(credentials, update=True)

    assert auser
    assert auser.login == oldlogin
    assert auser.password != oldpassw
    alg, cost, hashed = user.password.split('$')
    assert alg == 'bcrypt'


# -----------------------------------------------------------------------------

def get_test_env(path='/', **kwargs):
    builder = EnvironBuilder(path=path, **kwargs)
    return builder.get_environ()


def get_test_request(path='/', **kwargs):
    env = get_test_env(path, **kwargs)
    return Request(env)
