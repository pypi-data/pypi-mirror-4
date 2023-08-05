#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Helper classes and functions for various tasks"""
# (c) 2012 Ville Korhonen <ville@xd.fi>

import sys

import requests
import requests_cache

#import simplejson as json
import json

from lxml import html

CACHE_DEFAULT_TIMEOUT = 600 # 600 seconds, ie. 10 minutes
HTTP_DEFAULT_METHOD = 'GET'

def json_handler(obj):
    """Handle unknown formats when converting python objects to json"""
    # datetime.datetime
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError, "".join(['Object of type %s with value of ',
            '%s is not JSON serializable']) % (type(obj), repr(obj))

class ScraperMissingElementError(Exception):
    """HTML elements missing"""
    pass

class ScraperFetchError(Exception):
    """HTTP error"""
    pass

class Scraper(object):
    """Base class for building advanced web scraping apps"""
    def __init__(self, name=None, *args, **kwargs):
        self._name = name
        self._stats = {
            'fetched': 0,
        }

        if 'cache_time' in kwargs:
            cache_time = kwargs['cache_time'] / 60
        else:
            cache_time = CACHE_DEFAULT_TIMEOUT / 60
        requests_cache.configure(self._name, expire_after=cache_time)

    def _fetch(self, url, method='GET', *args, **kwargs):
        """Execute actual HTTP query using requests library"""
        t_method = method.lower()

        # TODO: submit also URL parameters or POST data payload if specified
        if t_method == 'get':
            response = requests.get(url)
        elif t_method == 'post':
            response = requests.post(url)
        else:
            raise ValueError, "".join([
                'Invalid fetch method %s, ',
                'possibly not implemented yet'
            ]) % t_method

        self._add_to_stats('fetched')

        return response.text

    def _add_to_stats(self, s_type):
        """Update stats"""
        if self._stats.has_key(s_type):
            self._stats[s_type] += 1
        else:
            self._stats[s_type] = 1
        return self._stats[s_type]

    def add_queue(self, url):
        """Add job to queue"""
        raise NotImplementedError

    def process_queue(self):
        """Start processing queue"""
        raise NotImplementedError

    def get(self, url, *args, **kwargs):
        """Fetch given URL using HTTP GET"""
        return self._fetch(url, method='get', *args, **kwargs)

    def post(self, url, *args, **kwargs):
        """Fetch given URL using HTTP POST"""
        return self._fetch(url, method='post', *args, **kwargs)

    def parse(self, url, parser, callback=None, format=None,
        method=HTTP_DEFAULT_METHOD, *args, **kwargs):
        """Parse given URL using parser and return results"""
        response = self._fetch(url, method=method)
        parsed = parser(response, *args, **kwargs)

        if 'limit' in kwargs and kwargs['limit'] > 0 and len(parsed) > 1:
            parsed = parsed[0:int(kwargs['limit'])]

        if callback:
            callback(parsed)
        else:
            if format == 'json':
                return json.dumps(parsed, default=json_handler)
            return parsed

# opts = {'throttle': "50/60',} # 50 queries in 60 seconds
# s = Scraper(name='koaschat', baseurl='http://ypcs.fi/data', opts)
# users = s.parse('sample.json', parser=get_users)
# s.add_queue(['sample1.json', 'sample2.json', 'sample3.json', 'sample4.json'])
# s.add_queue([{'url':'sample5.json', 'callback': add_events,
# 'parser': parse_events,}])
# s.process_queue()

def html_title_parser(content, *args, **kwargs):
    """Parse page title from HTML source"""
    doc = html.fromstring(content)
    title = doc.xpath('/html/head/title/text()')
    if len(title) == 0:
        raise ScraperMissingElementError, 'Document doesnt have html/head/title'
    else:
        return title[0]
    return title

def main(args):
    """CLI"""
    scraper = Scraper(name='scrapetool')

    if len(args) == 1:
        url = args[0]
        title = scraper.parse(url, parser=html_title_parser)
        print title
        return 0
    return 1


def run():
    """Run main() and return"""
#    parser = argparse.ArgumentParser(description="Scraping Tool")
    args = sys.argv[1:]
#    args = parser.parse_args()
    sys.exit(main(args) or 0)

if __name__ == "__main__":
    run()
