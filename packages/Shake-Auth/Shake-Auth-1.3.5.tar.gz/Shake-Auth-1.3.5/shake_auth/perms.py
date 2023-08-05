# -*- coding: utf-8 -*-
"""
Permission system & Cross Site Request Forgery protection.

This extension provides easy-to-use protection against [Cross Site
Request Forgeries][]. This type of attack occurs when a malicious web
site creates a link or form button that is intended to perform some
action on your Web site, using the credentials of a logged-in user who
is tricked into clicking on the link in their browser.

[Cross Site Request Forgeries]: http://en.wikipedia.org/wiki/Cross-site_request_forgery

## How to Use

1.  In any view that uses a POST form, use the CSFR global
    variable inside the <form\> element if the form is for an internal
    URL, e.g.:

        <form action="" method="post">
            …
            {{ csrf.input }}
        </form>

    This should *not* be done for forms that target external URLs,
    since that would cause the CSRF token to be leaked, leading to a
    vulnerability.

2.  If the corresponding view function is decorated with
    `@protected()` the CSFR token will be automatically
    checked. If no CSFR token is found or its value is incorrect, the
    decorator will raise a :class:`shake.NotAllowed` error.

    If you aren’t using the decorator or prefer to do the check
    manually, you can disable this feature by passing a `csrf=False
    parameter to the decorator, and using the function 'invalid_csrf'
    to validate the token, e.g.:

        from shake import NotAllowed
        from shake_auth import protected, invalid_csrf
        
        @protected(csrf=False)
        def myview(request):
            if invalid_csrf(request):
                raise NotAllowed()
            ...

    For those rare cases when you need to check the CSFR token for all
    request methods (eg. GET), pass the parameter `csrf=True` to the decorator.


## AJAX

To use the CSRF protection with AJAX calls insert the token in your
HTML template, as a javascript variable, and read it later from your script,
e.g.:

    <script>
    var CSRF_TOKEN = '{{ csrf_token.value }}';
    </script>

and later, in your javascript code:

    $.post(‘/theurl’, {
        … your data …
       '_csrf': CSRF_TOKEN
    });

Additionally, Shake-Auth accept the CSRF token in the custom HTTP header
X-CSRFToken, as well as in the form submission itself, for ease of use
with popular JavaScript toolkits which allow insertion of custom headers
into all AJAX requests.

The following example using the jQuery JavaScript toolkit demonstrates
this; the call to jQuery’s ajaxSetup will cause all AJAX requests to
send back the CSRF token in the custom X-CSRFTOKEN header:

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            var isAbsoluteUrl = /^[a-z0-9]+:\/\/.*/.test(settings.url);
            // Only send the token to relative URLs i.e. locally.
            if (! isAbsoluteUrl) {
                xhr.setRequestHeader("X-CSRFToken", CSRF_TOKEN);
            }
        }
    });

"""
from shake import redirect, NotAllowed, url_for, get_csrf


__all__ = (
    'REDIRECT_FIELD_NAME', 'protected', 'invalid_csrf', 'invalid_csrf_secret',
)


REDIRECT_FIELD_NAME = 'next'


def _login_required(request, sign_in_url=None, redirect_to=None):
    redirect_to = redirect_to or request.url
    request.session[REDIRECT_FIELD_NAME] = redirect_to
    sign_in_url = sign_in_url or url_for('auth.sign_in')
    if callable(sign_in_url):
        sign_in_url = sign_in_url(request)
    sign_in_url = sign_in_url or '/'
    return redirect(sign_in_url)


def protected(test=None, sign_in_url=None, csrf=None):
    """Factory of decorators for limit the access to views.
    
    test
    :   A function that takes the request and returns `True` or `False`. If it
        return `False`, a `NotAllowed` exception is raised.
    
    sign_in_url
    :   If any required condition fail, redirect to this place.
        Override the default url_for('auth.sign_in').
        This can also be a callable.
    
    csrf
    :   If `None` (the default), the decorator will check the value of the CSFR
        token only for POST request.
        If `True`, the check will be made for GET, POST, PUT and DELETE requests.
        If `False`, the value of the CSFR token will not be checked.
    
    """
    
    def real_decorator(target):
        
        def wrapped(request, **kwargs):
            user = getattr(request, 'user', None)
            if not user:
                return _login_required(request, sign_in_url)
            
            test_fail = (test is not None) and (not test(request, **kwargs))
            if test_fail:
                raise NotAllowed()
            
            # CSRF protection
            if csrf is not False:
                is_post = request.is_post
                is_others = request.method in ('GET', 'PUT', 'DELETE')
                if is_post or (csrf is True and is_others):
                    if invalid_csrf(request):
                        raise NotAllowed()
            
            return target(request, **kwargs)
        
        return wrapped
    
    return real_decorator


def is_valid(request, csrf=True):
    if not request.user:
        return False
    # CSRF protection
    if csrf and request.is_post and invalid_csrf(request):
        raise NotAllowed()
    return True


def invalid_csrf(request):
    valid_csrf_token = get_csrf(request)
    csrf_token = request.values.get(
        valid_csrf_token.name,
        request.headers.get('X-CSRFToken'))
    return csrf_token != valid_csrf_token.value

invalid_csrf_secret = invalid_csrf

