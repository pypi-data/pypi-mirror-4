""" Quickmeme processor --http://www.quickmeme.com/--

    Quickmeme doesnt provide oEmbed support
    Let's rip it apart

    Normal link: http://www.quickmeme.com/meme/352890/
    With some vars: http://www.quickmeme.com/meme/7fzt/#by=ad
    Image: http://i.qkme.me/7fzt.jpg
    Thumb: http://t.qkme.me/7fzt.jpg
"""
from urlparse import urlparse
import re

def lookup(url, **kwargs):
    normal = re.search('quickmeme.com', url)
    direct = re.search('qkme.me', url)
    if not normal and not direct:
        return None
    pr = urlparse(url)
    path = pr.path
    if normal:
        pic_id = re.search('\/\w+\/$', path).group()[1:-1]
    elif direct:
        pic_id = re.search('(?P<pic_id>\w+)(.jpg)?$', path).group('pic_id')
    else:
        raise ValueError("Can't parse your URL %s" % url)

    normal_url = 'http://www.quickmeme.com/meme/%s/' % pic_id
    direct_url = 'http://i.qkme.me/%s.jpg' % pic_id
    thumb_url = 'http://t.qkme.me/%s.jpg' % pic_id

    res = {
        'type': 'photo',
        'version': '1.0',
        'provider_name': 'quickmeme.com',
        'provider_url': 'http://www.quickmeme.com',
        'thumbnail_url': thumb_url,
        'quickmeme_page': normal_url,
        'url': direct_url,
        'width': None,
        'height': None,
        }

    return res