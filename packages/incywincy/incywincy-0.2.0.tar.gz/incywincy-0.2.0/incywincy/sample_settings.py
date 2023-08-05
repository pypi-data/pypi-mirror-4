from incywincy.visitors import http_errors, absolute_links


# user, password = 'user', 'password'


def nature(page):
    print('Nature! [{0}]'.format(page.url))


visitors = (
    ('.*', http_errors),
    ('.*', absolute_links),
    (r'^/nature', nature),
)
