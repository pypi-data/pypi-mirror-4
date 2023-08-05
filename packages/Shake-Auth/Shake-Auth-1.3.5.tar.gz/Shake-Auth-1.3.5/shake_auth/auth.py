# -*- coding: utf-8 -*-
"""
Shake-Auth

"""
from datetime import datetime
import hashlib
import hmac
import time

from jinja2 import ChoiceLoader
from jinja2.exceptions import TemplateNotFound
from shake import (url_for, from36, to36, redirect_to, Rule, StorageDict,
    to_bytestring, Render)

try:
    import mailshake
except ImportError:
    pass

from .perms import REDIRECT_FIELD_NAME, is_valid
from .utils import (bcrypt, scrypt, split_hash, generate_salt, pbkdf2,
    hash_sha256, hash_sha512, hash_bcrypt, hash_scrypt, get_user_hmac,
    LazyUser, Token, auth_loader)


__all__ = (
    'Auth', 'CREDENTIAL_LOGIN', 'CREDENTIAL_PASSWORD', 'CREDENTIAL_TOKEN',
    'UserExistsError', 'UserDoesNotExistsError', 'PasswordTooShortError'
)

CREDENTIAL_LOGIN = 'login'
CREDENTIAL_PASSWORD = 'password'
CREDENTIAL_TOKEN = 'token'


class UserExistsError(ValueError):
    
    def __init__(self, login):
        self.login = login
    
    def __repr__(self):
        return "A user with the login '%s' already exists." % self.login


class UserDoesNotExistsError(ValueError):
    
    def __init__(self, login):
        self.login = login
    
    def __repr__(self):
        return "User '%s' not found." % self.login


class PasswordTooShortError(ValueError):
    
    def __init__(self, minlen):
        self.minlen = minlen
    
    def __repr__(self):
        return ("The password is too short. It must be at least "
            "%s chars long." % self.minlen)


class Auth(object):
    """The authentication class.
    
    User
    :   an User model.
        
    app
    :   a Shake instance. Can be added later by calling `auth.init_app`.

    settings
    :   named settings. The following settings are available.
    

    ## Settings
    
    pepper
    :   required.
        A hardcoded (meaning "not stored in the database") system-wide
        secret 'salt'.
        
        By using this, an attacker would need to gain access to both
        the database and the filesystem (where your settings file is)
        in order to start trying an off-line attack.
        
        **You cannot change this value if there are already stored passwords
        or they all will become invalid**.
    
    hash_alg
    :   the name of the hashing algorithm, this can be one of the following:
        'bcrypt', 'sha512' or 'sha256'. If None, we use the best function
        available.
    
    hash_cost
    :   non-negative integer that control the cost of the hash algorithm.
        The number of operations is proportional to 2**cost.
    
    sign_in_redirect
    :   where to redirect the user, after signing in.
        This can be a callable.
    
    sign_out_redirect
    :   where to redirect the user, after signing out.
        This can be a callable.
        Ignored if `sign_out_view` is not None.

    password_minlen
    :   minimum number of chars the password must have.
        A `PasswordTooShortError` will be raised if it does not follow
        this limit.

    reset_expire
    :   number of hours after the reset-password one time use token become
        invalid.  This number can be a float to indicate a fraction of an
        hour (e.g.: 0.5 = 30 minutes).
    
    sign_in_template
    :   template used to render the sign in form.
    
    sign_out_template
    :   template rendered after the user sign out.
        
    change_password_template
    :   template udes to render the "Forgot your password?" form.
    
    reset_password_template
    :   template to render when resetting a password.
    
    email_reset_template
    :   template to use to send the reset-password email.

    render
    :   a render instance (used in all auth controllers)

    mailer
    :   a mailer instance (used in the reset password controller)
    
    ------------
    NOTE:
    The passwords hashes are stored with the following
    format (without the spaces):
        
        dsha512 $ cost $ salt $ salted_and_hashed_password
        - or -
        bcrypt $ cost $ salt salted_and_hashed_password

    """
    
    defaults = {
        'pepper': None,
        'hash_alg': None,
        'hash_cost': 11,

        'sign_in_redirect': '/',
        'sign_out_redirect': '/',
        'password_minlen': 5,
        'reset_expire': 3,  # hours

        'sign_in_template': 'auth/sign_in.html',
        'sign_out_template': None,
        'reset_password_template': 'auth/reset_password.html',
        'email_reset_template': 'auth/email_reset_password.html',
        'change_password_template': 'auth/change_password.html',

        'render': None,
        'mailer': None,
    }

    LazyUser = LazyUser
    
    def __init__(self, User, app=None, **settings):
        self.User = User
        self.db = User.db
        
        settings = StorageDict(settings)
        for k, default in self.defaults.items():
            settings.setdefault(k, default)
        
        assert settings.pepper is not None, "A `pepper` setting is required"
        settings.pepper = settings.pepper.encode('utf8', 'ignore')

        hash_alg = settings.hash_alg
        
        if not hash_alg:
            if scrypt:
                self.hash_func = hash_scrypt
                settings.hash_alg = 'scrypt'
            elif bcrypt:
                self.hash_func = hash_bcrypt
                settings.hash_alg = 'bcrypt'
            else:
                self.hash_func = hash_sha512
                settings.hash_alg = 'sha512'
        
        elif hash_alg == 'scrypt':
            if not scrypt:
                raise ImportError("Hash algorithm 'scrypt' not available")
            self.hash_func = hash_scrypt

        elif hash_alg == 'bcrypt':
            if not bcrypt:
                raise ImportError("Hash algorithm 'bcrypt' not available")
            self.hash_func = hash_bcrypt
        
        elif hash_alg == 'sha512':
            self.hash_func = hash_sha512
        
        elif hash_alg == 'sha256':
            self.hash_func = hash_sha256
        
        else:
            raise AssertionError("The `hash_alg` parameter must be either " \
                "'scrypt', 'bcrypt', 'sha512' or 'sha256'")
        
        hash_cost = settings.hash_cost or 4
        assert isinstance(hash_cost, (int, long)) and hash_cost >= 4, \
            "`hash_cost` parameter must be a positive integer bigger than 4"
        
        if (hash_alg == 'bcrypt') and (hash_cost < 4):
            settings.hash_cost = 4
        
        assert settings.reset_expire >= 0, \
            "`reset_expire` parameter must be a positive number"
        
        self.render = settings.pop('render', None)
        self.auth_render = None
        self.mailer = settings.pop('mailer', None)
        self.settings = settings
        if app:
            self.init_app(app)
        if self.render:
            self.init_render()
    
    def init_app(self, app):
        """This method can be used to initialize an application for the
        use with this authentication setup.
        """
        self.app = app
        self.render = self.render or app.render
        self.init_render()
        
        @app.before_request
        def set_user(request, **kwargs):
            self.get_user(request)

    def init_render(self):
        loader = ChoiceLoader([
            self.render.env.loader,
            auth_loader,
        ])
        self.auth_render = Render(loader=loader)

        self.auth_render.env.globals.update(self.render.env.globals)
        self.auth_render.env.filters.update(self.render.env.filters)
        self.auth_render.env.tests.update(self.render.env.tests)

        self.auth_render.response_class = self.render.response_class
        self.auth_render.default_mimetype = self.render.default_mimetype

    def render_to_string(self, template, context):
        try:
            return self.render(template, context, to_string=True)
        except TemplateNotFound:
            return auth_render(template, context, to_string=True)


    def get_user_by_login(self, login):
        """Get user by login (case-insensitive).
        """
        login = login.lower()
        lower_ = self.db.func.lower
        return self.db.query(self.User) \
            .filter(lower_(self.User.login) == login.lower()).first()

    def get_user(self, request):
        request.__class__.user = self.LazyUser(self.app, self.db, self.User)


    def authenticate(self, credentials, update=True):
        """Check if there's a matching pair of login/hashed_password in the
        database.
        
        If `update` is True and the authentication was successful, update the
        password hash to the current algorithm and cost.

        Returns the user if the credentials are correct, or None.
        """
        login = credentials.get(CREDENTIAL_LOGIN)
        password = credentials.get(CREDENTIAL_PASSWORD)
        if login and password:
            login = to_bytestring(login)
            password = to_bytestring(password)
            return self._loginpass_authentication(login, password, update)
        
        token = credentials.get(CREDENTIAL_TOKEN)
        if token:
            token = to_bytestring(token)
            return self._token_authentication(token)

    def _loginpass_authentication(self, login, password, update):
        user = self.get_user_by_login(login)
        if not user:
            return None
        if not self.check_password(password, user.password):
            return None
        
        if update:
            # If the authentication was successful, update the password hash
            # to the current algorithm and cost.
            hash_alg, hash_cost, salt = split_hash(user.password)
            must_update_hash = (hash_alg != self.settings.hash_alg)
            must_update_cost = (hash_cost != self.settings.hash_cost)
            if must_update_hash or must_update_cost:
                user.password = self.hash_password(password)
        return user

    def _token_authentication(self, token):
        try:
            login, time36, mac = token.split('.')
        except ValueError:
            return None
        
        user = self.get_user_by_login(login)
        if not user:
            return None
        
        # Check that the user/timestamp has not been tampered with
        retoken = self.get_reset_token(user, time36)
        if str(retoken) != token:
            return None
        
        timestamp = from36(time36)
        # Check if the token has not expired
        if (time.time() - timestamp) > (self.settings.reset_expire * 3600):
            return None
        
        return user

    def hash_password(self, password):
        password += self.settings.pepper
        hashed = self.hash_func(password, cost=self.settings.hash_cost)
        return hashed

    def check_password(self, password, stored_password):
        """Returns a boolean of whether the password is correct.
        
        Handles hashing behind the scenes.
        """
        if stored_password is None:
            return False

        stored_password = to_bytestring(stored_password)
        password += self.settings.pepper
        try:
            hash_alg, hash_cost, salt = split_hash(stored_password)
        except ValueError:
            raise ValueError("The stored password isn't a valid hash")

        if hash_alg == 'scrypt':
            assert 'scrypt' in globals().keys(), ('\'scrypt\' is not '
                'available but the stored password was hashed using it.\n '
                'Please install scrypt '
                '<http://pypi.python.org/pypi/scrypt/>')
            hashed = hash_scrypt(password, salt, hash_cost)

        elif hash_alg == 'bcrypt':
            assert 'bcrypt' in globals().keys(), ('\'bcrypt\' is not '
                'available but the stored password was hashed using it.\n '
                'Please install py-bcrypt '
                '<http://pypi.python.org/pypi/py-bcrypt/>')
            hashed = hash_scrypt(password, stored_password, hash_cost)

        elif hash_alg == 'dsha512':
            hashed = hash_sha512(password, salt, hash_cost)
        
        elif hash_alg == 'dsha256':
            hashed = hash_sha256(password, salt, hash_cost)

        elif hash_alg == 'sha512':
            hashed = hash_old_sha512(password, salt, hash_cost)

        elif hash_alg == 'sha256':
            hashed = hash_old_sha256(password, salt, hash_cost)
        
        else:
            raise ValueError("Hash algorithm '%s' not available" % hash_alg)

        return stored_password == hashed

    def set_password(self, user, passw):
        if len(passw) < self.settings.password_minlen:
            raise PasswordTooShortError(self.settings.password_minlen)
        user.password = self.hash_password(passw)

    def get_reset_token(self, user, time36=None):
        """Make a timestamped one-time-use token that can be used to
        identifying the user.
        
        By hashing on the internal state of the user that is sure to
        change (the password salt and the last_sign_in)
        we produce a token that will be invalid as soon as it or the
        old password is used.
        
        We hash also a secret key, so without access to the source code,
        fake tokens cannot be generated even if the database is compromised.
        """
        time36 = time36 or to36(int(time.time()))
        key = ''.join([
            self.app.settings.SECRET_KEY,
            getattr(user, 'password', '')[10:50],
            unicode(getattr(user, 'last_sign_in', '')),
            unicode(getattr(user, 'id', 0)),
            unicode(time36),
        ])
        key = key.encode('utf8', 'ignore')
        mac = hmac.new(key, msg=None, digestmod=hashlib.sha512)
        mac = mac.hexdigest()[:50]
        token = '%s.%s.%s' % (user.login, time36, mac)
        return Token(token, self.settings.reset_expire)

    def sign_in(self, request, user):
        request.session[self.LazyUser.SESSION_NAME] = get_user_hmac(user)
        request.user = user

    def sign_out(self, request):
        self.app.session_interface.invalidate(request)
        request.user = None


    def create_user(self, login, passw, **data):
        """[-login] USER_NAME [-passw] PASSWORD
        Creates a new user.
        This method is intended to be called from the command line.
        """
        login = to_bytestring(login)
        passw = to_bytestring(passw)
        user_exists = self.get_user_by_login(login)
        if user_exists:
            raise UserExistsError(login)
        user = self.User(login=login, password='', **data)
        self.db.add(user)
        self.set_password(user, passw)
        self.db.commit()
        return user
    
    def change_password(self, login, passw):
        """[-login] USER_NAME [-passw] NEW_PASSWORD
        Changes the password of an existing user.
        This method is intended to be called from the command line.
        """
        login = to_bytestring(login)
        passw = to_bytestring(passw)
        user = self.get_user_by_login(login)
        if not user:
            raise UserDoesNotExistsError(login)
        self.set_password(user, passw)
        self.db.commit()
        return user


    def sign_in_view(self, request, **kwargs):
        """Signs a user in.
        """
        redirect_url = request.session.get(REDIRECT_FIELD_NAME)
        redirect_url = redirect_url or self.settings.sign_in_redirect
        if callable(redirect_url):
            redirect_url = redirect_url()
        
        # Redirect if there's already a signed user
        if request.user:
            request.session.pop(REDIRECT_FIELD_NAME, None)
            return redirect_to(redirect_url)
        
        credentials = request.form
        kwargs['auth'] = self
        kwargs['credentials'] = credentials
        kwargs['error'] = None
        
        if request.is_post:
            user = self.authenticate(credentials)
            if user:
                if hasattr(user, 'last_sign_in'):
                    user.last_sign_in = datetime.utcnow()
                    self.db.commit()
                self.sign_in(request, user)
                return redirect_to(redirect_url)
            kwargs['error'] = 'FAIL'
        
        template = self.settings.sign_in_template
        return self.auth_render(template, kwargs)

    def sign_out_view(self, request, **kwargs):
        """Signs out a user.
        
        """
        redirect_url = self.settings.sign_out_redirect
        if callable(redirect_url):
            redirect_url = redirect_url()
        
        self.sign_out(request)
        
        template = self.settings.sign_out_template
        if template:
            kwargs['auth'] = self
            return self.auth_render(template, kwargs)
        return redirect_to(redirect_url)

    def reset_password_view(self, request, token=None, **kwargs):
        """A apge to generate a link to reset your password.
        
        token
        :   optional timestamped one-time-use token.
        
        """
        kwargs['auth'] = self
        kwargs['credentials'] = request.form
        kwargs['ok'] = False
        kwargs['error'] = None
        
        if not token and request.user:
            return redirect_to(url_for('auth.change_password'))
        
        # Phase 3
        if token:
            credentials = {CREDENTIAL_TOKEN: token}
            user = self.authenticate(credentials)
            if user:
                if request.user and (request.user != user):
                    self.sign_out(request)
                self.sign_in(request, user)
                return self.change_password_view(request, user_requested=False)
            
            kwargs['error'] = 'WRONG TOKEN'
        
        # Phase 2
        elif request.is_post:
            login = request.form.get('login', '')
            user = self.get_user_by_login(login)
            if not user:
                kwargs['error'] = 'NOT FOUND'
            else:
                # User founded. Send token by email
                site_name = self.app.settings.get('SITE_NAME')
                site_name = site_name or getattr(request, 'host')
                token = self.get_reset_token(user)
                self.email_token(user, token, site_name)
                kwargs['ok'] = True
        
        template = self.settings.reset_password_template
        return self.auth_render(template, kwargs)

    def email_token(self, user, token, site_name):
        assert self.mailer
        template = self.settings.email_reset_template
        msg = self.auth_render(template, {
            'user': user,
            'token': token,
            'site_name': site_name,
        }, to_string=True)
        msg = to_bytestring(msg)

        email_msg = mailshake.EmailMessage(
            subject='Reset your password',
            text_content='',
            from_email=self.mailer.default_from,
            to=user.email
        )
        if template.endswith('.html'):
            email_msg.html_content = msg
        else:
            email_msg.text_content = msg

        self.mailer.send(email_msg)

    def change_password_view(self, request, user_requested=True, **kwargs):
        """A view to change your password.
        """
        if not is_valid(request):
            return redirect_to(url_for('auth.sign_in'))
        
        sign_in_redirect = self.settings.sign_in_redirect
        if callable(sign_in_redirect):
            sign_in_redirect = sign_in_redirect()
        
        kwargs['auth'] = self
        kwargs['user_requested'] = user_requested
        kwargs['sign_in_redirect'] = sign_in_redirect
        kwargs['ok'] = False
        kwargs['errors'] = []
        
        if request.is_post:
            data = request.form
            password = to_bytestring(data.get('password', ''))
            np1 = to_bytestring(data.get('new_password_1', ''))
            np2 = to_bytestring(data.get('new_password_2', ''))
            
            # Validate the new password
            if len(np1) < self.settings.password_minlen:
                kwargs['errors'].append('TOO SHORT')
            
            if (not np2) or (np1 != np2):
                kwargs['errors'].append('MISMATCH')
            
            # Validate the current password
            user = request.user
            if user_requested and not \
                    self.check_password(password, user.password):
                kwargs['errors'].append('FAIL')
            
            if not kwargs['errors']:
                user.password = self.hash_password(np1)
                self.db.commit()
                # Refresh the user hmac in the session
                self.sign_in(request, user)
                kwargs['ok'] = True
        
        template = self.settings.change_password_template
        return self.auth_render(template, kwargs)

    sign_in_controller = sign_in_view
    sign_out_controller = sign_out_view
    change_password_controller = change_password_view
    reset_password_controller = reset_password_view

