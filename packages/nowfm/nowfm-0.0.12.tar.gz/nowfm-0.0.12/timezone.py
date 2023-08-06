# -*- coding: utf-8 -*-

import datetime


class UTC(datetime.tzinfo):
    # UTCからの時間のずれ
    def utcoffset(self, dt):
        return datetime.timedelta(hours=0)

    # サマータイム
    def dst(self, dt):
        return datetime.timedelta(0)

    # タイムゾーンの名前
    def tzname(self, dt):
        return 'UTC'

    # printしたときにUTCと統一感を持たせるため
    def __repr__(self):
        return '<UTC>'


utc = UTC()
