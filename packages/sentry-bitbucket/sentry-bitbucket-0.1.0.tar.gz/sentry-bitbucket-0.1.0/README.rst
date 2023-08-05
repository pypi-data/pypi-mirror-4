sentry-bitbucket
=============

An extension for Sentry which integrates with Bitbucket. Specifically, it
allows you to easily create issues from events within Sentry.


Install
-------

Install the package via ``pip``::

    pip install sentry-bitbucket

Ensure you've configured Bitbucket auth in Sentry::

    # Bitbucket needs to be included as a valid auth provider
    SENTRY_AUTH_PROVIDERS = {
        'twitter': ('TWITTER_CONSUMER_KEY', 'TWITTER_CONSUMER_SECRET'),
        'facebook': ('FACEBOOK_APP_ID', 'FACEBOOK_API_SECRET'),
        'github': ('GITHUB_APP_ID', 'GITHUB_API_SECRET'),
        'google': ('GOOGLE_OAUTH2_CLIENT_ID', 'GOOGLE_OAUTH2_CLIENT_SECRET'),
        'trello': ('TRELLO_API_KEY', 'TRELLO_API_SECRET'),
        'bitbucket': ('BITBUCKET_CONSUMER_KEY', 'BITBUCKET_CONSUMER_SECRET'),
    }

    # https://bitbucket.org/account/user/<username>/api
    BITBUCKET_OAUTH_KEY = ''
    BITBUCKET_OAUTH_SECRET = ''

Associate your account with Bitbucket (if you haven't already) via Account -> Identities.

You'll now see a new action on groups which allows quick creation of Bitbucket issues.


Caveats
-------

If you have multiple Bitbucket identities associated in Sentry, the plugin will just select
one to use.
