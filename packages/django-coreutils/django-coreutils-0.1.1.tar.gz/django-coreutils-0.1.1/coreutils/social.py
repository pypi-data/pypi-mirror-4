# coding: utf8

import json

from django.conf import settings


def do_facebook_post(token, message, message_type='feed'):
    from facebook import GraphAPI
    return json.loads(
        GraphAPI(token).put_object('me', message_type, message=message)
    )


def do_twitter_post(token, token_secret, message,
                    consumer_key=settings.TWITTER_CONSUMER_KEY,
                    consumer_secret=settings.TWITTER_CONSUMER_SECRET):
    import twitter
    api = twitter.Api(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token_key=token,
        access_token_secret=token_secret
    )
    return api.PostUpdate(message).__dict__
