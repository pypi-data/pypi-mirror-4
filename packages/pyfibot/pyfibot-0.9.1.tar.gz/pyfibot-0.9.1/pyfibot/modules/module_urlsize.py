"""
Warns about large files

$Id: module_urlsize.py 331 2012-11-13 10:18:18Z riku.lindblad@gmail.com $
$HeadURL: https://pyfibot.googlecode.com/svn/trunk/pyfibot/modules/module_urlsize.py $
"""


def handle_url(bot, user, channel, url, msg):
    """inform about large files (over 5MB)"""

    # TODO: Hard-coded
    if channel == "#wow":
        return
    size = getUrl(url).getSize()
    headers = getUrl(url).getHeaders()
    if 'content-type' in headers:
        contentType = headers['content-type']
    else:
        contentType = "Unknown"
    if not size:
        return
    size = size / 1024
    if size > 5:
        return bot.say(channel, "File size: %s MB - Content-Type: %s" % (size, contentType))
