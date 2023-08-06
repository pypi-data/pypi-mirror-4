from urlparse import urlparse
from oembed import Consumer, NoEndpointError
import re


IFRAME_EMBED_CODE = """<iframe class="youtube-player" type="text/html" width="%(width)s" height="%(height)s" src="http://www.youtube.com/embed/%(video_id)s" frameborder="0">
</iframe>"""

def lookup(url, **kwargs):
    consumer = Consumer(
        [
            ('http://youtube.com/watch*', 'http://www.youtube.com/oembed'),
            ('http://youtu.be/*', 'http://www.youtube.com/oembed'),
        ]
    )
    try:
        res = consumer.lookup(url, **kwargs)
    except NoEndpointError:
        return None

    # hack the <iframe> version for html embed code
    # let there be dragons
    video_id = None
    pr = urlparse(url)
    if 'youtube.com' in url:
        query = pr.query
        sre = re.search('v=(?P<id>[A-Za-z0-9_-]*)', query)
        if sre:
            try:
                video_id = sre.group('id')
            except IndexError:
                pass
    elif 'youtu.be' in url:
        path = pr.path
        sre = re.search('[A-Za-z0-9_-]*$', path)
        if sre:
            video_id = sre.group()
    else:
        pass
    if video_id:
        res['html_iframe'] = IFRAME_EMBED_CODE % ({'width': res['width'],'height': res['height'], 'video_id': video_id})
    return res