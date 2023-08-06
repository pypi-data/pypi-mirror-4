# -*- coding:utf-8 -*-
"""
Last.fmで現在再生中の曲の情報を取得するためのユーティリティ

Last.fmの仕様で現在再生中の曲について、再生開始時刻が取得できないので、
1つ前の曲の再生開始時刻+1つ前の曲の演奏時間と、現在時刻の古い方を
現在再生中の曲の再生開始時刻として利用する。

使い方
>>> fm = Nowfm('API KEY')
>>> now_track = fm.get_nowplaying('USER NAME')
"""

# python
import urllib
import json
import datetime
import time

import pytz


class Nowfm(object):
    endpoint = 'http://ws.audioscrobbler.com/2.0/'

    def __init__(self, api_key):
        self.api_key = api_key
        self.url_template = '{0}?api_key={1}&format=json'.format(
            Nowfm.endpoint, api_key)

    def get_nowplaying(self, user):
        """
        ユーザーの現在再生中の曲を再生開始時刻情報を付加して返す
        """
        method = 'user.getrecenttracks'
        url = self.url_template + '&method={0}&limit=1&user={1}'.format(
            method, user)
        jobj = json.loads(urllib.urlopen(url).read())
        tracks = jobj['recenttracks']['track']
        if type(tracks) is not list:
            return None
        now = tracks[0]
        if '@attr' not in now:
            return None
        self._set_date(now, tracks[1])
        return now

    def _set_date(self, now, prev):
        """
        現在再生中の曲の再生開始時刻を設定

        1つ前の曲の再生終了時刻は
        1つ前の曲の再生開始時刻+1つ前の曲の演奏時間で求められる

        現在再生中の曲の再生開始時刻は
        計算した1つ前の曲の再生終了時刻と現在時刻の古い方で近似値を求める
        (理由:現在の曲の再生開始時刻が未来にはならないから)

        arguments
        now: 現在再生中の曲
        prev: 1つ前の曲
        """
        now_uts = time.time()
        # 1つ前の曲の再生開始時刻のタイムスタンプ
        prev_start = int(prev['date']['uts'])
        # 1つ前の曲の演奏時間
        prev_duration = int(self._get_track_info(prev)['duration']) / 1000
        # 1つ前の曲の再生終了時刻のタイムスタンプ
        prev_end = prev_start + prev_duration
        # 現在の曲の再生開始時刻のタイムスタンプ
        now_start = min(prev_end, now_uts)
        now['date'] = {'#text': self._format_date(now_start), 'uts': now_start}

    def _get_track_info(self, track):
        """
        user.getrecenttracksで取得した曲の部分的な情報から
        track.getInfoを使って曲の完全な情報を取得する

        mbidという曲ごとに一意な値が利用できる場合はそれを利用し、
        利用できない場合は、アーティスト名と曲名を使って取得する

        argument
        track: 曲情報
        """
        method = 'track.getInfo'
        url = self.url_template + '&method={0}'.format(method)
        mbid = track['mbid']
        if mbid != '':
            url += '&mbid={0}'.format(mbid)
        else:
            url += '&track={0}&artist={1}'.format(
                track['name'], track['artist']['#text'])
        jobj = json.loads(urllib.urlopen(url).read())
        return jobj['track']

    def _format_date(self, uts):
        """
        曲の再生開始時刻を表す文字列をLast.fmの形式に合わせて整形する
        UNIX timestamp -> UTC datetime -> formatted UTC datetime
        """
        d = datetime.datetime.fromtimestamp(uts, tz=pytz.utc)
        return d.strftime('%d %b %Y, %H:%M')
