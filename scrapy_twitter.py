# coding:utf-8

from scrapy import log
from scrapy.http import Request, Response

import twitter


class TwitterUserTimelineRequest(Request):

    def __init__(self, *args, **kwargs):
        self.screen_name = kwargs.pop('screen_name', None)
        self.count = kwargs.pop('count', None)
        self.since_id = kwargs.pop('since_id', None)
        self.max_id = kwargs.pop('max_id', None)
        super(TwitterUserTimelineRequest, self).__init__('https://twitter.com',
                                                         dont_filter=True,
                                                         **kwargs)

class TwitterUserShowRequest(Request):

    def __init__(self, *args, **kwargs):
        self.screen_name = kwargs.pop('screen_name', None)
        self.user_id = kwargs.pop('user_id', None)
        self.include_entities = kwargs.pop('include_entities', False)
        super(TwitterUserShowRequest, self).__init__('https://twitter.com',
                                                     dont_filter=True,
                                                     **kwargs)

class TwitterStreamFilterRequest(Request):

    def __init__(self, *args, **kwargs):
        self.track = kwargs.pop('track', None)
        super(TwitterStreamFilterRequest, self).__init__('https://twitter.com',
                                                         dont_filter=True,
                                                         **kwargs)


class TwitterResponse(Response):

    def __init__(self, *args, **kwargs):
        self.tweets = kwargs.pop('tweets', None)
        self.user = kwargs.pop('user', None)
        super(TwitterResponse, self).__init__('https://twitter.com',
                                              *args,
                                              **kwargs)


class TwitterDownloaderMiddleware(object):

    def __init__(self,
                 consumer_key, consumer_secret,
                 access_token_key, access_token_secret,
                 tweet_mode,
                 proxies):
        self.api = twitter.Api(consumer_key=consumer_key,
                               consumer_secret=consumer_secret,
                               access_token_key=access_token_key,
                               access_token_secret=access_token_secret,
                               tweet_mode=tweet_mode,
                               proxies=proxies)
        log.msg('Using creds [CONSUMER KEY: %s, ACCESS TOKEN KEY: %s]' %
                (consumer_key, access_token_key),
                level=log.INFO)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        consumer_key = settings['TWITTER_CONSUMER_KEY']
        consumer_secret = settings['TWITTER_CONSUMER_SECRET']
        access_token_key = settings['TWITTER_ACCESS_TOKEN_KEY']
        access_token_secret = settings['TWITTER_ACCESS_TOKEN_SECRET']
        tweet_mode = settings['TWITTER_TEXT_MODE']
        proxies = settings['PROXIES']
        if tweet_mode is None:
            tweet_mode = 'compat'
        return cls(consumer_key,
                   consumer_secret,
                   access_token_key,
                   access_token_secret,
                   tweet_mode,
                   proxies)

    def process_request(self, request, spider):

        if isinstance(request, TwitterUserTimelineRequest):
            tweets = self.api.GetUserTimeline(screen_name=request.screen_name,
                                              count=request.count,
                                              since_id=request.since_id,
                                              max_id=request.max_id)
            return TwitterResponse(tweets=[tweet.AsDict() for tweet in tweets])

        if isinstance(request, TwitterUserShowRequest):
            return TwitterResponse(user=self.api.GetUser(include_entities=request.include_entities,
                                                         screen_name=request.screen_name,
                                                         user_id=request.user_id).AsDict())

        if isinstance(request, TwitterStreamFilterRequest):
            tweets = self.api.GetStreamFilter(track=request.track)
            return TwitterResponse(tweets=tweets)

    def process_response(self, request, response, spider):
        return response


from scrapy.item import DictItem, Field


def to_item(dict_tweet):
    field_list = dict_tweet.keys()
    fields = {field_name: Field() for field_name in field_list}
    item_class = type('TweetItem', (DictItem,), {'fields': fields})
    return item_class(dict_tweet)
