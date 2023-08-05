# -*- encoding: utf-8 -*-
import json
import urllib2

from rigcollector.collector import Collector

class SlushsPoolCollector(Collector):
    """
    Basic collector to call Slush's Mining Pool API
    https://mining.bitcoin.cz 
        -> My account 
        -> Manage API tokens 
        -> token
    """
    def __init__(self, conf):
        Collector.__init__(self, conf)
        self.api_url = "https://mining.bitcoin.cz/accounts/profile/json/{}".format(self.conf.get("token"))
        self.data = json.loads(urllib2.urlopen(self.api_url).read())
        
    def get_hashrate(self):
        return dict(name="Hashrate", data=dict(hashrate=float(self.data["hashrate"])))

    def get_reward(self):
        return dict(name="Reward", data=dict(reward=float(self.data["confirmed_reward"])))

    def get_all(self):
        return dict(custom=[self.get_hashrate(), self.get_reward()])
