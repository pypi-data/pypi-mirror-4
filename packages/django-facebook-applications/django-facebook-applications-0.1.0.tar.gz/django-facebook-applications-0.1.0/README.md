# Django Facebook Graph API Applications

[![Build Status](https://travis-ci.org/ramusus/django-facebook-applications.png?branch=master)](https://travis-ci.org/ramusus/django-facebook-applications) [![Coverage Status](https://coveralls.io/repos/ramusus/django-facebook-applications/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-facebook-applications)

Application for interacting with Facebook Graph API Applications objects using Django model interface

## Installation

    pip install django-facebook-applications

Add into `settings.py` lines:

    INSTALLED_APPS = (
        ...
        'oauth_tokens',
        'facebook_api',
        'facebook_applications',
    )

    # oauth-tokens settings
    OAUTH_TOKENS_HISTORY = True                                        # to keep in DB expired access tokens
    OAUTH_TOKENS_FACEBOOK_CLIENT_ID = ''                               # application ID
    OAUTH_TOKENS_FACEBOOK_CLIENT_SECRET = ''                           # application secret key
    OAUTH_TOKENS_FACEBOOK_SCOPE = ['offline_access']                   # application scopes
    OAUTH_TOKENS_FACEBOOK_USERNAME = ''                                # user login
    OAUTH_TOKENS_FACEBOOK_PASSWORD = ''                                # user password