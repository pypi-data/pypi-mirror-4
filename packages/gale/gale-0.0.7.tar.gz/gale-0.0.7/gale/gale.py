import urllib
import tornado.ioloop
import tornado.httputil
import time
import tornado.httpclient
from urlparse import urlparse
from functools import partial

tornado.httpclient.AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
'''
auth=(username, password)
proxy='user:pass@8.8.8.8:80'
'''
def start():
    tornado.ioloop.IOLoop.instance().start()

def stop():
    tornado.ioloop.IOLoop.instance().stop()

def sleep(seconds, callback):
    tornado.ioloop.IOLoop.instance().add_timeout(time.time() + seconds, callback)

def get(url, callback, params=None, cookies=None, headers={}, proxy=None, auth=None):
    request = generate_request(url, method='GET', params=params, cookies=cookies,
            headers=headers, proxy=proxy, auth=auth)
    http_client = tornado.httpclient.AsyncHTTPClient()
    return http_client.fetch(request, callback)

def post(url, callback, data, cookies=None, headers={}, proxy=None, auth=None):
    request = generate_request(url, method='POST', data=data, cookies=cookies,
            headers=headers, proxy=proxy, auth=auth)
    http_client = tornado.httpclient.AsyncHTTPClient()
    return http_client.fetch(request, callback)

def generate_request(url, method='GET', headers={}, cookies=None, proxy=None,
        auth=None, params=None, data=None):
    request_url = tornado.httputil.url_concat(url, params)
    proxy_username, proxy_password, proxy_host, proxy_port = parse_proxy(proxy)
    auth_username, auth_password = parse_auth(auth)
    request_headers = tornado.httputil.HTTPHeaders(headers)
    request_headers.update(parse_cookies(cookies))
    body = parse_data(data)
    request = tornado.httpclient.HTTPRequest(url = request_url,
                                             method = method,
                                             headers = request_headers,
                                             body = body,
                                             auth_username = auth_username,
                                             auth_password = auth_password,
                                             proxy_username = proxy_username,
                                             proxy_password = proxy_password,
                                             proxy_host = proxy_host,
                                             proxy_port = proxy_port)
    return request

def parse_data(data):
    if data is None:
        return None
    try:
        return urllib.urlencode(data)
    except:
        return data

def parse_proxy(proxy):
    if proxy is None:
        return None, None, None, None
    result = urlparse('//'+proxy)
    return result.username, result.password, result.hostname, result.port

def parse_auth(auth):
    if auth is None:
        return None, None
    return auth[0], auth[1]

def parse_cookies(cookies):
    if cookies is None:
        return {}
    return {'Cookie': ','.join(['%s=%s' % (k, cookies[k]) for k in cookies])}

class Task():

    def __init__(self):
        self.num = 0
        self.callback = None
        self.tasks = []

    def generate_task(self, func, *args, **kwargs):
        _origin_callback = kwargs.pop('callback')
        return partial(func,
               callback=partial(self.task_callback, _origin_callback=_origin_callback),
               *args, **kwargs)

    def task_callback(self, *args, **kwargs):
        _origin_callback = kwargs.pop('_origin_callback')
        _origin_callback(*args, **kwargs)
        self.task_done()

    def task_done(self):
        self.num -= 1
        if self.num == 0:
            self.callback()

    def add(self, func, *args, **kwargs):
        self.tasks.append(self.generate_task(func, *args, **kwargs))

    def patch(self, func):
        def wrapper(*args, **kwargs):
            self.add(func, *args, **kwargs)
        return wrapper

    def run(self, callback):
        self.num = len(self.tasks)
        self.callback = callback
        for task in self.tasks:
            task()
