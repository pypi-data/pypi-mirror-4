.. django-embed documentation master file, created by
   sphinx-quickstart on Tue Apr 23 14:09:15 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-embed's documentation!
========================================

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Install
=======

The simplest way to install django-embed is with pip.

::

	pip install django-embed

If you are using MySQL o PostgreSQL you have to change the encode for utf-8 of the embed_code column in the embed_embedcache. Ex. Using MySQL.

::

    ALTER TABLE <database>.embed_embedcache MODIFY COLUMN embed_code LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci;

Add "embed" to INSTALLED_APPS in your django settings.

::

    INSTALLED_APPS = (
        ...
        'embed',
    )


Usage
=====
Authentication
--------------
If you want to use the twitter embed code you have to provide the consumer and access keys.

::

    from embed.utils import Embed

    Embed.consumer_key = 'dummy-consumer-key'
    Embed.consumer_secret = 'dummy-consumer-secret'
    Embed.oauth_token = 'dummy-access-token'
    Embed.oauth_token_secret = 'dummy-access-token-secret'


Configuration
-------------
You can set the parameters for the embed code with the each api parameters. Except the size.
The size is the same for all the services and you can configure it like this.

::

    Embed.config = {
        'height': '300',
        'width': '400',
    }

For youtube parameters please refer to `Youtube API Parameters <https://developers.google.com/youtube/player_parameters?playerVersion=HTML5#Parameters>`_.

For twitter parameters please refer to `Twitter GET Embed <https://dev.twitter.com/docs/api/1.1/get/statuses/oembed>`_.

For slideshare parameters please refer to `Slideshare Embed Query Parameters <http://es.slideshare.net/developers/oembed>`_. 


Getting youtube embed code
--------------------------

Only you need to pass the string with the link and the django-embed will replace it with the embed code.

::

    s = 'Check this video https://youtu.be/THgLyTucjmk'
    embed_string = Embed.get_youtube_embed(string=s)


Getting twitter embed code
--------------------------

You can use twitter embed code in two ways.

Sending an id
~~~~~~~~~~~~~
Sending the twitter status id and receive the embed code.

::

    id = '99530515043983360'
    embed_code = Embed.get_twitter_embed_by_id(id=id)

Sending a string 
~~~~~~~~~~~~~~~~~
Sending a string with the tweet link and receive the string whit the embed code
::

    s = 'This tweet is so cool! https://twitter.com/twitter/status/99530515043983360'
    embed_string = Embed.get_twitter_embed(string=s)


Getting slideshare embed code
-----------------------------
Send a string with the slideshare link and receive the string with the link replaced by the embed code.

::

    s = 'The slides for business quotes http://www.slideshare.net/haraldf/business-quotes-for-2011'
    embed_string = Embed.get_slideshare_embed(string=s)


Getting all services embed code
-------------------------------
Send a string with links of youtube, twitter and/or slideshare.

::

    s = 'Check this video https://youtu.be/THgLyTucjmk. This tweet is so cool! https://twitter.com/twitter/status/99530515043983360. Oh! and this is thhe slides for business quotes http://www.slideshare.net/haraldf/business-quotes-for-2011'
    embed_string = Embed.get_all(string=s)



