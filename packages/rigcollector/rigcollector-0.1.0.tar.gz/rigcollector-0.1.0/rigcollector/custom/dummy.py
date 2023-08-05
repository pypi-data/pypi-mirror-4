import logging
from rigcollector.collector import Collector

logger = logging.getLogger(__name__)

class DummyCollector(Collector):
    """
    Minimal custom collector example
    """

    def __init__(self, conf):
        Collector.__init__(self, conf)
        # Do some things here
        # self.my_conf_key = self.conf.get("my_conf_key", "default_value") 
        # logger.info("my custom collector initialized")

    def get_mymetric(self):
        """
        An example method wich return a dummy metric1
        Data can contains any number of data
        Metrics values must be int, float, or long
        """
        return dict(name="mymetric", data=dict(metric1=10))

    def get_all(self):
        """
        A custom collector must have get_all method,
        and must return a dict with a unique key: custom,
        wich contains a list of metrics data
        """
        return dict(custom=[self.get_mymetric()])
