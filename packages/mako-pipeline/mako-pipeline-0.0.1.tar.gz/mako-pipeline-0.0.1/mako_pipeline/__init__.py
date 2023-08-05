# coding: utf-8

ASSETS = {
    'debug': False,
    'media_url': '/',
}


def configure(data=None):
    if data:
        ASSETS.update(data)
    return ASSETS
