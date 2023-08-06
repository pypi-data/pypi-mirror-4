# Django Facebook Graph API Users

[![Build Status](https://travis-ci.org/ramusus/django-facebook-users.png?branch=master)](https://travis-ci.org/ramusus/django-facebook-users) [![Coverage Status](https://coveralls.io/repos/ramusus/django-facebook-users/badge.png?branch=master)](https://coveralls.io/r/ramusus/django-facebook-users)

Application for interacting with Facebook Graph API Users objects using Django model interface

## Installation

    pip install django-facebook-users

Add into `settings.py` lines:

    INSTALLED_APPS = (
        ...
        'oauth_tokens',
        'facebook_api',
        'facebook_users',
    )

    # oauth-tokens settings
    OAUTH_TOKENS_HISTORY = True                                        # to keep in DB expired access tokens
    OAUTH_TOKENS_FACEBOOK_CLIENT_ID = ''                               # application ID
    OAUTH_TOKENS_FACEBOOK_CLIENT_SECRET = ''                           # application secret key
    OAUTH_TOKENS_FACEBOOK_SCOPE = ['offline_access']                   # application scopes
    OAUTH_TOKENS_FACEBOOK_USERNAME = ''                                # user login
    OAUTH_TOKENS_FACEBOOK_PASSWORD = ''                                # user password

## Usage examples

### Fetch user by Graph ID

    >>> from facebook_users.models import User
    >>> user = User.remote.fetch(4)
    >>> user
    <User: Mark Zuckerberg>
    >>> user.__dict__
    {'_external_links_post_save': [],
     '_external_links_to_add': [],
     '_foreignkeys_post_save': [],
     '_state': <django.db.models.base.ModelState at 0xdf4514c>,
     'bio': '',
     'birthday': '',
     'cover': {'id': '989690200741',
      'offset_y': 0,
      'source': 'http://m.ak.fbcdn.net/sphotos-a.ak/hphotos-ak-ash4/s720x720/311205_989690200741_1231438675_n.jpg'},
     'currency': None,
     'devices': None,
     'education': None,
     'email': '',
     'favorite_athletes': None,
     'favorite_teams': None,
     'first_name': 'Mark',
     'gender': 'male',
     'graph_id': '4',
     'hometown': None,
     'id': 11214,
     'installed': None,
     'interested_in': None,
     'languages': None,
     'last_name': 'Zuckerberg',
     'link': 'http://www.facebook.com/zuck',
     'locale': 'en_US',
     'location': None,
     'middle_name': '',
     'name': 'Mark Zuckerberg',
     'payment_pricepoints': None,
     'picture': '',
     'political': '',
     'quotes': '',
     'relationship_status': '',
     'religion': '',
     'security_settings': None,
     'significant_other': None,
     'third_party_id': '7joA1JrNkjG9e-A6yGLZyiTzdL4',
     'timezone': None,
     'updated_time': datetime.datetime(2013, 3, 13, 20, 36, 43, tzinfo=tzutc()),
     'username': 'zuck',
     'verified': False,
     'video_upload_limits': None,
     'website': '',
     'work': None}

### Fetch user by slug

    >>> from facebook_users.models import User
    >>> User.remote.fetch('zuck')
    <User: Mark Zuckerberg>