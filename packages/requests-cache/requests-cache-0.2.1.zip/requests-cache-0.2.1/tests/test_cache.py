#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Path hack
import os, sys
sys.path.insert(0, os.path.abspath('..'))

import unittest
import time
import json
from collections import defaultdict

import requests

import requests_cache
from requests_cache.compat import bytes, str, is_py3

CACHE_BACKEND = 'sqlite'
CACHE_NAME = 'requests_cache_test'
FAST_SAVE = False

if 'HTTPBIN_URL' not in os.environ:
    os.environ['HTTPBIN_URL'] = 'http://httpbin.org/'

HTTPBIN_URL = os.environ.get('HTTPBIN_URL')


def httpbin(*suffix):
    """Returns url for HTTPBIN resource."""
    return HTTPBIN_URL + '/'.join(suffix)

class CacheTestCase(unittest.TestCase):

    def setUp(self):
        requests_cache.configure(CACHE_NAME, backend=CACHE_BACKEND, fast_save=FAST_SAVE)
        requests_cache.clear()

    def test_speedup_and_undo_redo_patch(self):
        delay = 1
        def long_request():
            t = time.time()
            for i in range(5):
                r = requests.get(httpbin('delay/%s' % delay))
            delta = time.time() - t
            self.assertLess(delta, delay * 3)
        long_request()
        requests_cache.undo_patch()
        t = time.time()
        r = requests.get(httpbin('delay/%s' % delay))
        delta = time.time() - t
        self.assertGreaterEqual(delta, delay)
        requests_cache.redo_patch()
        long_request()

    def test_expire_cache(self):
        delay = 1
        url = httpbin('delay/%s' % delay)
        requests_cache.configure(CACHE_NAME, backend=CACHE_BACKEND, expire_after=0.001)
        t = time.time()
        r = requests.get(url)
        delta = time.time() - t
        self.assertGreaterEqual(delta, delay)
        time.sleep(0.5)
        t = time.time()
        r = requests.get(url)
        delta = time.time() - t
        self.assertGreaterEqual(delta, delay)

    def test_delete_urls(self):
        url = httpbin('redirect/3')
        r = requests.get(url)
        for i in range(1, 4):
            self.assert_(requests_cache.has_url(httpbin('redirect/%s' % i)))
        requests_cache.delete_url(url)
        self.assert_(not requests_cache.has_url(url))

    def test_unregistered_backend(self):
        with self.assertRaises(ValueError):
            requests_cache.configure(CACHE_NAME, backend='nonexistent')

    def test_async_compatibility(self):
        try:
            import grequests
        except Exception:
            self.skipTest('gevent is not installed')
        n = 3
        def long_running():
            t = time.time()
            rs = [grequests.get(httpbin('delay/%s' % i)) for i in range(n + 1)]
            grequests.map(rs)
            return time.time() - t
        # cache it
        delta = long_running()
        self.assertGreaterEqual(delta, n)
        # fast from cache
        delta = 0
        for i in range(n):
            delta += long_running()
        self.assertLessEqual(delta, 1)

    def test_hooks(self):
        state = defaultdict(int)
        for hook in ('response', 'post_request'):

            def hook_func(r):
                state[hook] += 1
                return r
            n = 5
            for i in range(n):
                r = requests.get(httpbin('get'), hooks={hook: hook_func})
            self.assertEqual(state[hook], n)

    def test_post(self):
        url = httpbin('post')
        r1 = json.loads(requests.post(url, data={'test1': 'test1'}).text)
        r2 = json.loads(requests.post(url, data={'test2': 'test2'}).text)
        self.assertIn('test2', r2['form'])
        self.assert_(not requests_cache.has_url(url))

    def test_disabled_enabled(self):
        delay = 1
        url = httpbin('delay/%s' % delay)
        with requests_cache.disabled():
            t = time.time()
            n = 2
            for i in range(n):
                requests.get(url)
            delta = time.time() - t
            self.assertGreaterEqual(delta, delay * n)

        with requests_cache.enabled():
            t = time.time()
            n = 5
            for i in range(n):
                requests.get(url)
            delta = time.time() - t
            self.assertLessEqual(delta, delay * n)

    def test_content_and_cookies(self):
        s = requests.session()
        def js(url):
            return json.loads(s.get(url).text)
        r1 = js(httpbin('cookies/set/test1/test2'))
        with requests_cache.disabled():
            r2 = js(httpbin('cookies'))
        self.assertEqual(r1, r2)
        r3 = js(httpbin('cookies'))
        with requests_cache.disabled():
            r4 = js(httpbin('cookies/set/test3/test4'))
        # from cache
        self.assertEqual(r3, js(httpbin('cookies')))
        # updated
        with requests_cache.disabled():
            self.assertEqual(r4, js(httpbin('cookies')))

    def test_response_history(self):
        r1 = requests.get(httpbin('redirect/3'))
        def test_redirect_history(url):
            r2 = requests.get(url)
            for r11, r22 in zip(r1.history, r2.history):
                self.assertEqual(r11.url, r22.url)
        test_redirect_history(httpbin('redirect/3'))
        test_redirect_history(httpbin('redirect/2'))
        with requests_cache.disabled():
            r3 = requests.get(httpbin('redirect/1'))
            self.assertEqual(len(r3.history), 1)

    def post(self, data):
        return json.loads(requests.post(httpbin('post'), data=data).text)

    def test_post_params(self):
        # issue #2
        requests_cache.configure(CACHE_NAME, CACHE_BACKEND, allowable_methods=('GET', 'POST'))

        for _ in range(3):
            d = {'param1': 'test1'}
            self.assertEqual(self.post(d)['form'], d)
            d = {'param1': 'test1', 'param3': 'test3'}
            self.assertEqual(self.post(d)['form'], d)
            d = {'param1': 'test1', 'param3': 'test3'}
            self.assertEqual(self.post(d)['form'], d)
            d = [('param1', 'test1'), ('param2', 'test2'), ('param3', 'test3')]
            res = sorted(self.post(d)['form'].items())
            self.assertEqual(res, d)

    def test_post_data(self):
        # issue #2, raw payload
        requests_cache.configure(CACHE_NAME, CACHE_BACKEND,
                                 allowable_methods=('GET', 'POST'))
        d1 = json.dumps({'param1': 'test1'})
        d2 = json.dumps({'param1': 'test1', 'param2': 'test2'})
        d3 = str('some unicode data')
        if is_py3:
            bin_data = bytes('some binary data', 'utf8')
        else:
            bin_data = bytes('some binary data')

        for d in (d1, d2, d3):
            self.assertEqual(self.post(d)['data'], d)
            r = requests.post(httpbin('post'), data=d)
            self.assert_(hasattr(r, 'from_cache'))

        self.assertEqual(self.post(bin_data)['data'],
                         bin_data.decode('utf8'))
        r = requests.post(httpbin('post'), data=bin_data)
        self.assert_(hasattr(r, 'from_cache'))

    def test_get_params_as_argument(self):
        for _ in range(5):
            p = {'arg1': 'value1'}
            r = json.loads(requests.get(httpbin('get'), params=p).text)
            self.assert_(requests_cache.has_url(httpbin('get?arg1=value1')))

    def test_https_support(self):
        n = 10
        delay = 1
        url = 'https://httpbin.org/delay/%s?ar1=value1' % delay
        t = time.time()
        for _ in range(n):
            r = json.loads(requests.get(url, verify=False).text)
            self.assert_(requests_cache.has_url(url))
        self.assertLessEqual(time.time() - t, delay * n / 2)

    def test_from_cache_attribute(self):
        url = httpbin('get?q=1')
        self.assert_(not hasattr(requests.get(url), 'from_cache'))
        self.assert_(hasattr(requests.get(url), 'from_cache'))
        requests_cache.delete_url(url)
        self.assert_(not hasattr(requests.get(url), 'from_cache'))




if __name__ == '__main__':
    unittest.main()
