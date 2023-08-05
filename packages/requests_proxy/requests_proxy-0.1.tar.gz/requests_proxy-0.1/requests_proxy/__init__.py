# -*- coding: utf-8 -*-
import requests


class Proxy(object):

    options = dict(verify=None, allow_redirects=False)

    def __init__(self, url, **kwargs):
        self.url = url.rstrip('/')
        options = self.options.copy()
        options.update(kwargs)
        self.options = options

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        if environ.get('QUERY_STRING'):
            path += '?' + environ.get('QUERY_STRING')
        headers = []
        for k, v in environ.items():
            if k[:5] == 'HTTP_':
                headers.append((k[5:].replace('_', '-').title(), v))
        kwargs = self.options.copy()
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        headers.append(('Content-Length', content_length))
        if content_length:
            kwargs['data'] = environ['wsgi.input'].read(content_length)
        meth = getattr(requests, environ['REQUEST_METHOD'].lower())
        resp = meth(self.url + path, **kwargs)
        headers = [(k.title(), v) for k, v in resp.headers.items()]
        start_response('%s %s' % (resp.status_code, resp.reason), headers)
        return resp.iter_content()
