import re
from urlparse import urljoin
from collections import deque

from bs4 import BeautifulSoup
import requests
from requests.auth import HTTPBasicAuth

from incywincy.config import settings
from incywincy.report import debug, error


UA = 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'
exceptions = []


def find_links(html):
    """
    Find all ``<a>`` links in the HTML page.
    """
    soup = BeautifulSoup(html)
    links = filter(lambda a: 'href' in a.attrs, soup.find_all('a'))
    return [a['href'] for a in links]


def normalised(links, start, base):
    """
    Return a set of normalised links.

    These will all be absolute URLs, and no repeats.
    """
    links = [urljoin(base, link) for link in links]
    return set(filter(lambda x: x.startswith(start), links))


class Page(object):
    """
    A web page, that can be processed by a visitor.

    Contains useful information about the page, such as the status code,
    content, list of links, and referrer (the page where we found a link to
    this one).
    """
    def __init__(self, url, referrer):
        self.referrer = referrer
        self.url = url
        headers = {'User-Agent': UA}
        self.response = requests.get(url, auth=settings.auth, headers=headers)
        self._links = []

    def __getattr__(self, attr):
        return getattr(self.response, attr)

    def __str__(self):
        if isinstance(self.referrer, Page):
            referrer_url = self.referrer.url
        else:
            referrer_url = self.referrer
        return "{url} [from: {ref}]".format(url=self.url, ref=referrer_url)

    @property
    def links(self):
        if not self._links:
            if self.response.status_code == 200:
                content_type = self.headers['Content-Type']
                if content_type.startswith('text/html'):
                    self._links = find_links(self.text)
                    # debug('Links: ' + ', '.join(self._links))
        return self._links

    def normalised_links(self, start):
        return normalised(self.links, start, self.url)


def visit(url, parent=None):
    """
    Recursively visit all pages from this URL.

    Will keep track of seen pages, so as to avoid processing links twice.
    """
    try:
        settings.auth = HTTPBasicAuth(settings.user, settings.password)
    except:
        settings.auth = None

    # Keep a queue of pending links, and a set of seen links
    pending = deque()
    seen = set()

    pending.append((url, parent))
    seen.add(url)
    total = 1

    # Main crawler loop
    while len(pending) > 0:
        url, parent = pending.popleft()
        debug('[{0},+{1}] Opening: {2}'.format(total, len(pending), url))
        try:
            page = Page(url, parent)
        except Exception as e:
            error('Exception in {0}: {1}'.format(url, e))
            exceptions.append({'url': url, 'error': e})
        else:
            for pattern, visitor in settings.visitors:
                url_path = url[len(settings.root):]
                if re.match(pattern, url_path):
                    visitor(page)
            # add new links to queue if successful
            if page.status_code == 200:
                links = page.normalised_links(settings.start)
                links.difference_update(seen)
                # debug("New links:\n" + "\n".join(links))
                for link in links:
                    pending.append((link, page))
                    seen.add(link)
                total += len(links)
