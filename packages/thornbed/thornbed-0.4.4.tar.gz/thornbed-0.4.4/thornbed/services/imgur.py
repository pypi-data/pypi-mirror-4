""" Imgur data processor

    Since Imgur doesn't provide oEmbed interface, we have to query data using
    their API, so this is a Wrapper for their API service.

    http://imgur.com/gallery/NiK0X
    http://imgur.com/BynR8
    http://i.imgur.com/BynR8.png
    http://i.imgur.com/BynR8s.png

    images can be png, jpg or gif

    json returned by imgur

    {
        "image":
            {
                "image": {
                            "title": null,
                            "caption": null,
                            "hash": "BynR8",
                            "datetime": "2011-08-30 23:45:13",
                            "type": "image\/jpeg",
                            "animated": "false",
                            "width": 500,
                            "height": 578,
                            "size": 75375,
                            "views": 358449,
                            "bandwidth": 27018093375
                            },
                "links": {
                            "original": "http:\/\/i.imgur.com\/BynR8.jpg",
                            "imgur_page": "http:\/\/imgur.com\/BynR8",
                            "small_square": "http:\/\/i.imgur.com\/BynR8s.jpg",
                            "large_thumbnail": "http:\/\/i.imgur.com\/BynR8l.jpg"
                         }
            }
    }
    
"""
from urlparse import urlparse
import re
import requests
from thornbed.version import version

imgur_endpoint = 'http://api.imgur.com/2/image/%s.json'

def lookup(url, **kwargs):
    pr = urlparse(url)
    path = pr.path
    # we are planning to support albums in a near future, not for now or not :P
    if not re.search('(i\.)?imgur.com', url) or re.search('imgur.com\/a\/', url):
        return None
    pattern = r"^https?:\/\/(www\.|i\.)?imgur\.com\/(gallery\/)?(?P<pid>\w{5,})(?P<ptype>\.gif|\.jpg|\.jpeg|\.png)?(\?full)?$"
    res = re.match(pattern, url)
    pid = res.group('pid') if res else None
    if not pid:
        return None
    if len(pid) > 5:
        pid = re.sub(r"(h|m|l|s)?$", '', pid)

    res = requests.get("http://imgur.com/%s?tags" % pid, headers={"User-Agent": "Thornbed/%s" % version})
    # now get the real pid and ptype from that page
    md = re.search('id\=\"nondirect\"[ ]+value\=\"http:\/\/imgur.com\/(?P<pid>\w{5,})', res.content)
    pid = md.group('pid') if md else None
    if not pid:
        return None
    md = re.search('id\=\"direct\"[ ]+value\=\"http://i.imgur.com/\w+(?P<ptype>\.jpg|\.jpeg|\.png|\.gif)', res.content)
    ptype = md.group('ptype') if md else '.jpg'

    # imgur pic_id is ambiguous since the chars for thumb etc... can be part of the id
    # so we check the embed page
    # first get the pseudo id

    # md = pattern.match(url)
    # pid = md[:pid]
    # # TODO: improve this code
    # if pid.length > 5
    # pid = pid.gsub(/(h|m|l|s)?$/, '')
    # end
    # raise Thornbed::NotValid, url if not pid
    #
    # res = HTTParty.get("http://imgur.com/#{pid}?tags", headers: {"User-Agent" => USER_AGENT})
    #
    # # now get the real pid and ptype from that page
    # md = /id\=\"nondirect\"[ ]+value\=\"http:\/\/imgur.com\/(?<pid>\w+)/.match(res.body)
    # pid = md[:pid]
    #
    # raise Thornbed::NotValid, url if not pid
    #
    # md = /id\=\"direct\"[ ]+value\=\"http:\/\/i.imgur.com\/\w+(?<ptype>\.jpg|\.jpeg|\.png|\.gif)/.match(res.body)
    # ptype = md[:ptype] || ".jpg"

    # thumbs are always .jpg
    thumbnail_url = 'http://i.imgur.com/%ss.jpg' % pid
    imgur_page = 'http://imgur.com/%s' % pid
    url = 'http://i.imgur.com/%s%s' % (pid, ptype)
    res = {
        'type': 'photo',
        'version': '1.0',
        'provider_name': 'imgur.com',
        'provider_url': 'http://imgur.com',
        'thumbnail_url': thumbnail_url,
        'imgur_page': imgur_page,
        'url': url,
        'width': '',
        'height': '',
        }

    return res
