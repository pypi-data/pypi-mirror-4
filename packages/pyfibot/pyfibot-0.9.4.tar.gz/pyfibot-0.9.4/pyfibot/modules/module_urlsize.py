"""
Warns about large files

$Id$
$HeadURL$
"""
from __future__ import unicode_literals, print_function, division
import requests


def handle_url(bot, user, channel, url, msg):
    """inform about large files (over 5MB)"""

    r = requests.head(url)
    size = r.headers['content-length']
    content_type = r.headers['content-type']
    if not content_type:
        content_type = "Unknown"
    if not size:
        return
    size = float(size) / 1024 / 1024
    # report files over 5 MB
    if size > 5:
        return bot.say(channel, "File size: %s MB - Content-Type: %s" % (int(size), content_type))
