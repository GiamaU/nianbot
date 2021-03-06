import datetime
import typing
from pathlib import Path

import discord
from discord.ext.commands import AutoShardedBot

from utils import dataIO
from .worker import WebWorker, InternalWorker


class NianBot(AutoShardedBot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = dataIO.get_Info('config.json')
        self.to_load: typing.List[str] = None

        self.ww = WebWorker(self)
        self.iw = InternalWorker(self)

        self.ww.dbh.set_db("kyo_server")

    async def on_ready(self):
        print(f'[*]Ready: {self.user} (ID: {self.user.id})')

        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        if not hasattr(self, 'main_guild'):
            self.main_guild = self.get_guild(684039093927280664)

        if not hasattr(self, 'log_channel'):
            self.log_channel = self.get_channel(696333346577317998)

        if not hasattr(self, 'warn_channel'):
            self.warn_channel = self.get_channel(727460706072526858)

        if not hasattr(self, 'videos_channel'):
            self.videos_channel = self.get_channel(684040996581015572)

        if not hasattr(self, 'news_channel'):
            self.news_channel = self.get_channel(684405119840026734)

        if not hasattr(self, 'questions_channel'):
            self.questions_channel = self.get_channel(735536160234930297)

        if not hasattr(self, 'answers_channel'):
            self.answers_channel = self.get_channel(735536183043424287)

        if self.config.status_type == "idle":
            status_type = discord.Status.idle
        elif self.config.status_type == "dnd":
            status_type = discord.Status.dnd
        elif self.config.status_type == "offline":
            status_type = discord.Status.offline
        else:
            status_type = discord.Status.online

        if self.config.playing_type == "listening":
            playing_type = 2
        elif self.config.playing_type == "watching":
            playing_type = 3
        else:
            playing_type = 0

        await self.change_presence(
            activity=discord.Activity(type=playing_type, name=self.config.playing),
            status=status_type
        )

        if not self.ww.is_running():
            self.ww.start()

        if not self.iw.is_running():
            self.iw.start_question_picker()

    async def on_guild_join(self, guild):
        if not self.config.join_message:
            return

        try:
            to_send = sorted([chan for chan in guild.channels if
                              chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)],
                             key=lambda x: x.position)[0]
        except IndexError:
            pass
        else:
            await to_send.send(self.config.join_message)

    def discover_exts(self, directory: str):
        ignore = {'__pycache__', '__init__'}

        exts = [
            p.stem for p in Path(directory).resolve().iterdir()
            if p.stem not in ignore
        ]

        print('Loading extensions: ', exts)

        for ext in exts:
            self.load_extension(f'{directory}.' + ext)

        self.to_load = list(self.extensions.keys()).copy()
