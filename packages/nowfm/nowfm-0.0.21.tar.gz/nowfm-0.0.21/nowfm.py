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
import urllib2
import json
import datetime
import time
import threading

import pytz

class NowfmError(Exception):
    def __init__(self, value, detail=""):
        self.value = value
        self.detail = detail

    def __str__(self):
        return repr(self.value)

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
        src = self._get_src(url)
        jobj = json.loads(src)
        tracks = jobj['recenttracks']['track']
        if type(tracks) is not list:
            raise NowfmError("{0} is not currently playing track".format(user),
                             'type(tracks) is not list')
        if len(tracks) < 2:
            raise NowfmError("{0} is not currently playing track".format(user),
                             "len(tracks) < 2")
        now, prev = tracks[0], tracks[1]
        ldate = []
        t1 = threading.Thread(target=self._thread_calc_date, args=(prev, ldate))
        t1.start()

        linfo = []
        t2 = threading.Thread(target=self._thread_get_track_info, args=(now, linfo))
        t2.start()
        t1.join()
        t2.join()

        info = linfo[0]
        date = ldate[0]
        if '@attr' in now:
            info['@attr'] = now['@attr']
        info['@date'] = date
        return info

    def _get_src(self, url):
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        f = opener.open(url)
        if f.getcode() == 404:
            raise NowfmError("404 Not Found")
        if f.info().gettype() == 'text/xml':
            raise NowfmError("503 Service Unavailable",
                             "Last.fm Server returns text/xml")
        return unicode(f.read(), 'utf-8')

    def _calc_date(self, prev):
        """
        現在再生中の曲の再生開始時刻を計算

        1つ前の曲の再生終了時刻は
        1つ前の曲の再生開始時刻+1つ前の曲の演奏時間で求められる

        現在再生中の曲の再生開始時刻は
        計算した1つ前の曲の再生終了時刻と現在時刻の古い方で近似値を求める
        (理由:現在の曲の再生開始時刻が未来にはならないから)

        arguments
        prev: 1つ前の曲
        """
        now_uts = time.time()
        # 1つ前の曲の再生開始時刻のタイムスタンプ
        prev_start = int(prev['date']['uts'])
        # 1つ前の曲の演奏時間
        prev_info = self._get_track_info(prev)
        prev_duration = int(prev_info['duration']) / 1000
        # 1つ前の曲の再生終了時刻のタイムスタンプ
        prev_end = prev_start + prev_duration
        # 現在の曲の再生開始時刻のタイムスタンプ
        now_start = min(prev_end, now_uts)
        return {'#text': self.format_date(now_start), 'uts': now_start}

    def _thread_calc_date(self, prev, ret):
        """
        _calc_dateをthread化するためのラッパー
        ret: thread用の戻り値を0番目に格納
        """
        ret.append(self._calc_date(prev))
        return

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
        src = self._get_src(url)
        jobj = json.loads(src)
        return jobj['track']

    def _thread_get_track_info(self, track, ret):
        """
        _get_track_infoをthread化するためのラッパー
        ret: thread用の戻り値を0番目に格納
        """
        ret.append(self._get_track_info(track))
        return

    def format_date(self, uts):
        """
        曲の再生開始時刻を表す文字列をLast.fmの形式に合わせて整形する
        UNIX timestamp -> UTC datetime -> formatted UTC datetime
        """
        d = datetime.datetime.fromtimestamp(uts, tz=pytz.utc)
        return d.strftime('%d %b %Y, %H:%M')
