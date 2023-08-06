=====
Embed
=====

Embed is a Django app to generate the embed code for youtube, twitter and slideshare.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "embed" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'embed',
      )

2. Run `python manage.py syncdb` to create the embed cache model.

3. Import Embed class.

      from embed.utils import Embed

3. You can use it individually for each service or all of them.

      youtube = Embed.get_youtube_embed(string="Check this video https://youtu.be/THgLyTucjmk")

4. The Embed will return a string with the link replaced with the embed code.

5. If you want use the twitter functionality you have to set your twitter api keys.

      Embed.consumer_key = 'dummy-consumer-key'
      Embed.consumer_secret = 'dummy-consumer-secret'
      Embed.oauth_token = 'dummy-access-token'
      Embed.oauth_token_secret = 'dummy-access-token-secret'

6. You can set the parameters for the embed objects.

      Embed.config['width'] = '430'

7. If you are using MySQL you need to encode to utf-8 the "embed_code" column of the EmbedCache table in your database.
