import os
from apiclient.discovery import build
import re


class YoutubeApiH:

    def __init__(self, channelID):
        self.youtube = build('youtube', 'v3', developerKey=os.getenv('yt_google_api_key'))
        self.channel_id = channelID

    def get_all_channel_videos(self):
        res = self.youtube.channels().list(
            id=self.channel_id,
            part='contentDetails'
        ).execute()

        playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        videos = []
        next_page_token = None

        while True:
            res = self.youtube.playlistItems().list(
                playlistId=playlist_id,
                part='snippet',
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for video in res['items']:
                videoId = video['snippet']['resourceId']['videoId']
                title = video['snippet']['title']
                videos.append(
                    {
                        'id': videoId,
                        'title': title
                    }
                )

            try:
                next_page_token = res['nextPageToken']
            except KeyError:
                break

            if next_page_token is None:
                break

        return videos

    def get_last_channel_videos(self, lastId):

        res = self.youtube.channels().list(id=self.channel_id, part='contentDetails').execute()

        playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        videos = []
        next_page_token = None

        while True:
            res = self.youtube.playlistItems().list(
                playlistId=playlist_id,
                part='snippet',
                maxResults=2,
                pageToken=next_page_token
            ).execute()

            for video in res['items']:
                videoId = video['snippet']['resourceId']['videoId']
                title = video['snippet']['title']
                if lastId is None or len(lastId) == 0:
                    return None
                elif videoId == lastId:
                    return videos
                else:
                    videos.append(
                        {
                            'id': videoId,
                            'title': title
                        }
                    )

            try:
                next_page_token = res['nextPageToken']
            except KeyError:
                break

            if next_page_token is None:
                break

        return videos

    def get_channel_videos(self, title, quantity: int = 10):

        videos = []
        next_page_token = None

        if title is None:
            return None

        while True:
            res = self.youtube.search().list(
                q=title,
                channelId=self.channel_id,
                part='snippet',
                type='video',
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for item in res['items']:
                video_title = re.sub(r'[\u3010-\u3011]', '', item['snippet']['title'])
                if title.lower() in video_title.lower():
                    videos.append(video_title)

            try:
                next_page_token = res['nextPageToken']
            except KeyError:
                break

            if next_page_token is None:
                break

        return videos[:quantity]

    def get_all_channel_playlists(self):

        playlists = []
        next_page_token = None

        while True:

            res = self.youtube.playlists().list(
                channelId=self.channel_id,
                part='snippet',
                maxResults=25,
                pageToken=next_page_token
            ).execute()

            for playlist in res['items']:
                playlistId = playlist['id']
                title = playlist['snippet']['title']
                playlists.append(
                    {
                        'playlistId': playlistId,
                        'title': title
                    }
                )

            try:
                next_page_token = res['nextPageToken']
            except KeyError:
                break

            if next_page_token is None:
                break

        return playlists

    def get_channel_playlists(self, title):

        playlists = []
        next_page_token = None

        while True:

            res = self.youtube.search().list(
                q='levels',
                channelId=self.channel_id,
                part='snippet',
                type='playlist',
                maxResults=25,
                pageToken=next_page_token
            ).execute()

            for playlist in res['items']:
                playlist_title = re.sub(r'[\u3010-\u3011]', '', playlist['snippet']['title'])
                if title.lower() in playlist_title.lower():
                    playlistId = playlist['id']
                    title = playlist['snippet']['title']
                    playlists.append(
                        {
                            'playlistId': playlistId,
                            'title': title
                        }
                    )

            try:
                next_page_token = res['nextPageToken']
            except KeyError:
                break

            if next_page_token is None:
                break

        return playlists
