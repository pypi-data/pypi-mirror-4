# coding: utf-8
from mako.runtime import supports_caller

from mako_pipeline import ASSETS


@supports_caller
def tag(context, name, **kwargs):
    media_url = ASSETS['media_url']
    if ASSETS.get('debug', False):
        files = ASSETS['javascript'][name]
    else:
        files = (name,)

    for filename in files:
        url = '{}{}.js'.format(media_url, filename)
        context['caller'].body(ASSETS_URL=url)

    return ''
