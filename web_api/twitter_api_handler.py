import tweepy
import os


class TwitterApiH:

    def __init__(self, userId):
        auth = tweepy.OAuthHandler(os.getenv('tw_consumer_key'), os.getenv('tw_consumer_secret'))
        auth.set_access_token(os.getenv('tw_access_key'), os.getenv('tw_access_secret'))

        self.api = tweepy.API(auth)

        self.userId = userId

    def get_all_user_tweets(self):

        tweets = []

        for status in tweepy.Cursor(self.api.user_timeline, id=self.userId).items():
            if hasattr(status, "entities"):
                entities = status.entities
                for url in entities['urls']:
                    url = url['expanded_url']
                    id = url.split('/')[-1]
                    tweets.append(
                        {
                            'url': url,
                            'id': id
                        }
                    )

        return tweets

    def get_last_user_tweets(self, lastId):

        tweets = []

        for status in tweepy.Cursor(self.api.user_timeline, id=self.userId).items():
            if hasattr(status, "entities"):
                entities = status.entities
                for url in entities['urls']:
                    url = url['expanded_url']
                    id = url.split('/')[-1]
                    if lastId is None or len(lastId) == 0:
                        return None
                    elif id == lastId:
                        return tweets
                    else:
                        tweets.append(
                            {
                                'url': url,
                                'id': id
                            }
                        )

        return tweets

    def get_last_tweet(self):
        tweets = []

        for status in tweepy.Cursor(self.api.user_timeline, id=self.userId).items():
            if hasattr(status, "entities"):
                entities = status.entities
                for url in entities['urls']:
                    url = url['expanded_url']
                    id = url.split('/')[-1]
                    tweets.append(
                        {
                            'url': url,
                            'id': id
                        }
                    )
                    return tweets

        return tweets
