from services import get_providers

providers = get_providers()

def embed(url, **kwargs):
    res = None
    for service, lookup in providers:
        res = lookup(url, **kwargs)
        if res:
            break
    return res