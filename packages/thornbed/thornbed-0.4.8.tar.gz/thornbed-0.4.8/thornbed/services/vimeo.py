from oembed import Consumer, NoEndpointError


def lookup(url, **kwargs):
    consumer = Consumer(
        [
            ('http://vimeo.com/*', 'http://www.vimeo.com/api/oembed.json'),
            ('http://vimeo.com/*', 'http://www.vimeo.com/api/oembed.json'),
            ('http://www.vimeo.com/groups/*/*', 'http://www.vimeo.com/api/oembed.json'),
            ('http://www.vimeo.com/groups/*/*', 'http://www.vimeo.com/api/oembed.json'),
        ]
    )
    try:
        res = consumer.lookup(url, **kwargs)
    except NoEndpointError:
        res = None
    return res