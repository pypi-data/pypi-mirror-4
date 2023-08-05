# -*- coding: utf-8 -*-
import requests
import json


def simple_callback(address, **data):
    """Simple callback function that uploads job-specific status data to a given address."""
    try:
        requests.post(address, data=json.dumps(data))
    except:
        pass


class curried_callback(object):
    def __init__(self, url):
        self.url = url
        self.failed = 0
        self.available = True

    def __call__(self, **kwargs):
        if not self.available:
            return
        try:
            requests.post(self.url, data=json.dumps(kwargs))
        except:
            # Error posting to collection daemon
            self.failed += 1
            if self.failed > 5:
                self.available = False
