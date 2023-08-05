from incywincy.config import settings
from incywincy.report import log, ERROR, WARNING


def http_errors(page):
    status = page.status_code
    if status >= 400:
        log(page, 'Status [{0}]'.format(status), ERROR)


def absolute_links(page):
    for link in page.links:
        if link.startswith(settings.root):
            log(page, 'Absolute internal URL [{0}]'.format(link), WARNING)


def redirects(page):
    if page.history:
        location = page.history[0].headers['location']
        log(page, 'Redirected to: {0}'.format(location), WARNING)
