=================
python-vimeo
=================

A python wrapper for using the `Vimeo API`_.

.. _Vimeo API: http://developer.vimeo.com/

Installation
------------

To install python-vimeo, simply: ::

    pip install vimeo

Or ::

    easy_install vimeo

Basic Use
---------

To use python-vimeo, you must first create a `Client` instance,
passing at a minimum of key, secret and callback you obtained when you `registered
your app`_: ::

    import vimeo
    
    client = vimeo.Client(key=YOUR_CONSUMER_KEY, secret=YOUR_CONSUMER_SECRET, callback=YOUR_CALLBACK_URL)

The client instance can then be used to fetch or modify resources: ::

    videos = client.get('vimeo.videos.getAll', user_id=11867661, page=1)

.. _registered your app: https://developer.vimeo.com/apps/new

Authentication
--------------

All `OAuth authorization flows`_ supported by the Vimeo API are
available in python-vimeo. If you only need read-only access to
public resources, go for basic use method as shown above. If however,
you need to access private resources or modify a resource,
you will need to have a user delegate access to your application. To do
this, you can use the following OAuth2 authorization flow.

**Authorization Code Flow**

The Authorization Code Flow involves redirecting the user to vimeo.com 
where they will log in and grant access to your application: ::

    import vimeo

    client = vimeo.Client(
        key='YOUR_CONSUMER_KEY',
        secret='YOUR_CONSUMER_SECRET',
        callback='YOUR_CALLBACK_URL',
	username='USERNAME_FROM_YOU_APP'
    )
    redirect(client.authorize_url())

Note that `username` should be the unique logged in username from your application.
The auth informations will be stored in the seperate cache for the specifed username.
And `callback` must match the value you provided when you
registered your application. After granting access, the user will be
redirected to this url, at which point your application can exchange
the returned token information for an access token. After getting the information just
pass the token verifier: ::

    token = client.exchange_token('TOKEN_VERIFIER')
    access_token = token.key
    access_token_secret = token.secret

.. _`OAuth authorization flows`: https://developer.vimeo.com/apis/advanced#oauth

Examples
--------

Get user's Authorization: ::

    import vimeo

    client = vimeo.Client(key=YOUR_CONSUMER_KEY, secret=YOUR_CONSUMER_SECRET, callback=YOUR_CALLBACK_URL, username='LOGGED IN USERNAME')
    redirect(client.authorize_url())

Get the authenticated user's uploaded videos: ::

    import vimeo

    client = vimeo.Client(key=YOUR_CONSUMER_KEY, secret=YOUR_CONSUMER_SECRET, callback=YOUR_CALLBACK_URL, username='LOGGED_IN_USERNAME', token=False)
    token = client.exchange_token('TOKEN_VERIFIER_FROM_THE_REDIRECTED_URL')
    client = vimeo.Client(key=YOUR_CONSUMER_KEY, secret=YOUR_CONSUMER_SECRET, callback=YOUR_CALLBACK_URL, username='LOGGED_IN_USERNAME', token=True)
    videos = client.get('vimeo.videos.getUploaded', page=1)


    
