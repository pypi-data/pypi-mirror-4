"""
urlhelp

Package init file
"""
import re
import os
from StringIO import StringIO
import urlparse

from lxml import html
import requests

from _version import __version__

__all__ = [
    'protocolise',
    'find_links'
    ]

def protocolise(url):
    """
    Given a URL, check to see if there is an assocaited protocol.

    If not, set the protocol to HTTP and return the protocolised URL
    """
    # Use the regex to match http//localhost/something
    protore = re.compile(r'https?:{0,1}/{1,2}')
    parsed = urlparse.urlparse(url)
    if not parsed.scheme and not protore.search(url):
        url = 'http://{0}'.format(url)
    return url

def find_links(url):
    """
    Find the href destinations of all links at  URL

    Arguments:
    - `url`:

    Return: list[str]
    Exceptions: None
    """
    url = protocolise(url)
    content = requests.get(url).content
    flike = StringIO(content)
    root = html.parse(flike).getroot()
    atags = root.cssselect('a')
    hrefs = [a.attrib['href'] for a in atags]
    # !!! This does the wrong thing for bbc.co.uk/index.html
    hrefs = [h if h.startswith('http') else '/'.join([url, h]) for h in hrefs ]
    return hrefs
