from oembed import Consumer, NoEndpointError, NotFoundError
import re


def lookup(url, **kwargs):
    consumer = Consumer(
        [
            ('http://*.flickr.com/*', 'http://www.flickr.com/services/oembed/'),
        ]
    )
    try:
        res = consumer.lookup(url, **kwargs)
    except NoEndpointError, NotFoundError:
        res = None

    # since our friends at flickr do not return the thumbnail_url,
    # we will hack it ourselves, thumbnails are always in .jpg format
    # http://www.flickr.com/services/api/misc.urls.html
    if res:
        sre = re.search('_[mstzb].(?P<ext>jpg|gif|png)', res['thumbnail_url'])
        if sre:
            thumb_url = '%s_t.jpg' % res['thumbnail_url'][:sre.start()]
            ext = sre.group('ext')
            # the image can be small, medium or whatever, we want original
            url = '%s.%s' % (res['thumbnail_url'][:sre.start()], sre.group('ext'))
            res['url'] = url
        else:
            thumb_url = '%s_t.jpg' % res['url'][:-4]

        res[u'thumbnail_url'] = thumb_url

    return res
