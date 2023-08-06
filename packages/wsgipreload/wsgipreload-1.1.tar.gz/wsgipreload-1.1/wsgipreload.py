import os
import re
from itertools import islice

import webob

pid = os.getpid()

environ_more_defaults = {
    'REMOTE_ADDR': '127.0.0.1',
}


def start_response(*a, **kw):
    pass


def request(app, url, extra_environ):
    print 'wsgipreload pid=%s: requesting %s' % (pid, url)
    environ = webob.Request.blank(url).environ
    environ.update(environ_more_defaults)
    if extra_environ:
        environ.update(extra_environ)
    a = app(environ, start_response)
    try:
        # read the contents from the iterator
        return ''.join(a)
    finally:
        if hasattr(a, 'close'):
            a.close()


def preload(app, urls, extra_environ=None):
    for url in urls:
        request(app, url, extra_environ)
    print 'wsgipreload pid=%s: done' % pid


def url_from_log_line(log, statuses=['200']):
    regex = r' "GET (.+?) HTTP/1.[0-9]" '
    if statuses:
        regex += '(%s) ' % '|'.join(statuses)
    match = re.search(regex, log)
    if match:
        return match.group(1)


def urls_from_log(log, num=10, max_check=100, statuses=['200'], url_filter=None):
    '''
    Given a log (e.g. an open file), parse and filter out URLs.
    Only GET requests are ever considered.
    '''
    urls = set()
    for log_line in islice(log, 0, max_check):
        url = url_from_log_line(log_line, statuses)
        if url:
            if (url_filter and url_filter(url)) or not url_filter:
                urls.add(url)
        if len(urls) >= num:
            break
    return urls

