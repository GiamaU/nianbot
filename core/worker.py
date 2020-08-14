from discord.ext import tasks
from datetime import datetime, timedelta
import asyncio
import random
from pymongo.errors import DuplicateKeyError
from pymongo.errors import BulkWriteError
from mongoengine import NotUniqueError
from web_api import youtube_api_handler as yth, twitter_api_handler as twh, db_api_handler as dbh

channelId = 'UCWwuijyo4x78iXup5hOvkbw'
twitterId = 1126470462777610241

youtube_search_url = 'https://www.youtube.com/watch?v='
youtube_playlist_url = 'https://www.youtube.com/playlist?list='

# todo fix qotd system + >paq (pick a question) command + better exceptions
# todo change restart with next.replace (better?)
# improve this system


class InternalWorker:  # todo do this better

    def __init__(self, bot):
        self.bot = bot
        self.actual_question = None

    def start_question_picker(self):
        print('[*]STARTING question picker process (InternalWorker)')

        self.pick_question.start()

    def stop_question_picker(self):
        print('[*]STOPPING question picker process (InternalWorker)')

        self.pick_question.stop()

    def restart_question_picker(self):
        print('[*]RESTARTING question picker process (InternalWorker)')

        self.pick_question.restart()

    def is_running(self):
        return self.pick_question.get_task()

    async def send_question(self):
        if self.actual_question is None:
            self.actual_question = await self.bot.answers_channel.history().flatten()[-1].jump_url
        await self.bot.answers_channel.send(f'```Markdown\n#QOTD:```\n<{self.actual_question}>')

    @tasks.loop(hours=24)
    async def pick_question(self):

        now = datetime.now()
        next = now + timedelta(hours=24)

        print(f'[*]trying to pick a question... {now}')
        try:
            messages = list(question for question in (await self.bot.questions_channel.history().flatten()) if '>qotd' in question.content.lower()[:5])
            if messages is not None and len(messages) > 0:
                print('[*]clearing channel...')
                await self.bot.answers_channel.purge()

                question = random.choice(messages)
                message = await self.bot.answers_channel.send(f'```Markdown\n#QOTD:```\n{question.content[6:]}')
                await message.add_reaction(chr(0x1F44D))
                await message.add_reaction(chr(0x1F44E))
                self.actual_question = message.jump_url
            else:
                raise Exception(f'No questions to pick, next try at {self.pick_question.next_iteration}')
        except Exception as e:
            print('[*]failed to pick a question RIP...', e)
        else:
            print(f'[*]successfully picked a question: {question.content[6:20]}... next pick at {self.pick_question.next_iteration}')
            await question.delete()

        now = datetime.now()
        interval = next - now
        interval = datetime.strptime(str(interval), "%H:%M:%S")  # bad solution?
        self.pick_question.change_interval(hours=interval.hour, minutes=interval.minute, seconds=interval.second)

    @pick_question.before_loop
    async def pick_question_before(self):
        now = datetime.now()
        next = datetime.now()
        next = next.replace(hour=12, minute=0, second=0)
        if next < now:
            next = next.replace(day=now.day + 1)
        await asyncio.sleep((next - now).total_seconds())


class WebWorker:

    def __init__(self, bot):
        self.yth = yth.YoutubeApiH(channelId)                                       # format: (youtube channel id)
        self.twh = twh.TwitterApiH(twitterId)                                       # format: (twitter channel id)
        self.dbh = dbh.dbApiH()                                                     # format: ()
        self.bot = bot

        self.last_youtube_id = None  # better in db?
        self.last_twitter_id = None  # better in db?

        print('[*]Ready Worker')

    def start(self):
        print('[*]STARTING worker')

        self.update_tweets.start()
        self.update_videos.start()

    def stop(self):
        print('[*]STOPPING worker')

        self.update_tweets.cancel()
        self.update_videos.cancel()

    def restart(self):  # delete -- better to replace time?
        print('[*]RESTARTING worker')

        self.update_tweets.restart()
        self.update_videos.restart()

    def is_running(self):
        return self.update_videos.get_task() and self.update_videos.get_task()

    def reset(self, name: str = None, type: str = None):

        if name is None:
            if type is not None and type == 'full':
                self.dbh.delete_all_documents('videos')
            self.last_twitter_id = None
            self.last_youtube_id = None
            self.update_tweets.restart()
            self.update_videos.restart()
        elif name == 'tweets':
            self.last_twitter_id = None
            self.update_tweets.restart()
        elif name == 'youtube':
            if type is not None and type == 'full':
                self.dbh.delete_all_documents('videos')
            self.last_youtube_id = None
            self.update_videos.restart()

    @tasks.loop(minutes=10)
    async def update_tweets(self):
        print('[*]updating tweets', datetime.utcnow().time())

        try:
            # todo do this better?
            tweets = []
            if self.last_twitter_id is None:
                tweets = self.twh.get_last_tweet()

                if tweets is None:
                    raise Exception('ERROR retrieving latest tweet')
            else:
                tweets = self.twh.get_last_user_tweets(self.last_twitter_id)
                if tweets is not None and 0 < len(tweets) < 5:
                    print('[*]sending new tweets...')

                    for tweet in reversed(tweets):
                        await self.bot.news_channel.send(f'New tweet!! \n{tweet["url"]}')
                elif len(tweets) > 5:
                    raise Exception('[*]ERROR retrieving latest tweetS')
                else:
                    print('[*]no new tweets found')

            if len(tweets) > 0:
                self.last_twitter_id = tweets[0]['id']
        except Exception as e:
            print('[*]ERROR updating tweets: ', e)
        else:
            print('[*]tweets updated SUCCESSfully')

        print(f'[*]next tweets update at {self.update_tweets.next_iteration}')

    @tasks.loop(minutes=10)
    async def update_videos(self):
        print('[*]updating videos', datetime.utcnow().time())

        try:
            # todo do this better?
            videos = []
            if self.last_youtube_id is None:
                videos = self.yth.get_all_channel_videos()

                if videos is None:
                    raise Exception('[*]ERROR retrieving all channel videos')
            else:
                videos = self.yth.get_last_channel_videos(self.last_youtube_id)

                if videos is not None and 0 < len(videos) < 5:
                    print('[*]sending youtube videos...')
                    for video in reversed(videos):
                        await self.bot.videos_channel.send(f'New video!! \n{youtube_search_url}{video["id"]}')
                elif len(videos) > 5:
                    raise Exception('ERROR retrieving new channel videos')
                else:
                    print('[*]no new videos found')

            if len(videos) > 0:
                self.last_youtube_id = videos[0]['id']
                self.dbh.add_videos(videos)
        except (NotUniqueError, DuplicateKeyError, BulkWriteError) as e:  # possible to catch only catch
            print('[*]Some videos ALREADY present in the db,', e)
        except Exception as e:
            print('[*]ERROR updating videos: ', e)
        else:
            print('[*]videos updated SUCCESSfully')

        print(f'[*]next videos update at {self.update_videos.next_iteration}')
