import click

from tm_downloader.utils.tm_client import parse_telegram_url, parse_url_from_pattern


class UrlType(click.ParamType):
    name = 'url'

    def convert(self, value, param, ctx):
        try:
            return parse_telegram_url(value)
        except Exception:
            self.fail('invalid url', param, ctx)

class UrlPatternType(click.ParamType):
    name = 'url'

    def convert(self, value, param, ctx):
        try:
            return parse_url_from_pattern(value)
        except Exception:
            self.fail('invalid url pattern', param, ctx)

URL = UrlType()
URLPATTERN = UrlPatternType()