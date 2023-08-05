# -*- encoding: utf-8 -*-
import json
import urllib2
from urllib import urlencode
import time
from hashlib import sha512
from hmac import HMAC
import base64

from rigcollector.collector import Collector


class MtGoxCollector(Collector):
    """
    Retrieve your MtGox BTC Balance
    https://mtgox.com/ 
        -> Security Center 
        -> Advanced API Key Creation 
        -> Rights: Get info

    """
    def __init__(self, conf):
        Collector.__init__(self, conf)
        self.auth_key = self.conf.get("auth_key")
        self.auth_secret = base64.b64decode(self.conf.get("auth_secret"))
 
    def get_nonce(self):
        return int(time.time()*100000)
 
    def sign_data(self, secret, data):
        return base64.b64encode(str(HMAC(secret, data, sha512).digest()))

    def build_query(self, req={}):
        req["nonce"] = self.get_nonce()
        post_data = urlencode(req)
        headers = {}
        headers["User-Agent"] = "GoxApi"
        headers["Rest-Key"] = self.auth_key
        headers["Rest-Sign"] = self.sign_data(self.auth_secret, post_data)
        return (post_data, headers)
 
    def get_btc_balance(self, path="generic/private/info", args={}):
        data, headers = self.build_query(args)
        req = urllib2.Request("https://mtgox.com/api/1/"+path, data, headers)
        res = urllib2.urlopen(req, data)
        res = json.load(res)
        return dict(name="MtGox", data=dict(balance=float(res["return"]["Wallets"]["BTC"]["Balance"]["value"])))

    def get_all(self):
        return dict(custom=[self.get_btc_balance()])
