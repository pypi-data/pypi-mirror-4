from incywincy.config import settings


broken = []


def http_errors(page):
    status = page.status_code
    if status >= 400:
        print('Status [{0}] for URL: {1}'.format(status, page))
        broken.append(page)


def absolute_links(page):
    for link in page.links:
        if link.startswith(settings.root):
            print('Found absolute internal URL [{0}] in: {1}'
                  .format(link, page.url))
