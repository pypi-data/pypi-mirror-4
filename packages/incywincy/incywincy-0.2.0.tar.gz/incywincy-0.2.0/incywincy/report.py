DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3

CRITICALITY = {
    DEBUG: 'DEBUG',
    INFO: 'INFO',
    WARNING: 'WARNING',
    ERROR: 'ERROR',
}

THRESHOLD = 1


def log(page, message, level=WARNING):
    if level >= THRESHOLD:
        print(">> {0}: {1} | {2}".format(CRITICALITY[level], message, page.url))


def debug(message):
    if THRESHOLD == DEBUG:
        print(message)


def error(message):
    print(message)
