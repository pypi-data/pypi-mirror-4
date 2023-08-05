# -*- encoding: utf-8 -*-
import re
import os
import subprocess
from string import split
import logging

logger = logging.getLogger(__name__)

ATI_CONFIG_PATH = '/usr/bin/aticonfig'

from rigcollector.collector import Collector

class AtiGpuCollector(Collector):
    """
    Makes use of aticonfig to retrieve gpus temperature
    Some posts on ths topics has been helpul if you need more
    informations: https://bitcointalk.org/index.php?topic=10062.0
    """

    def __init__(self, conf):
        Collector.__init__(self, conf)
        self.ati_config_path = self.conf.get("ati_config_path", ATI_CONFIG_PATH)

    def get_gpu_temp(self, gpuid):
        """
        Retrieve temperature for a specific GPU
        """
        os.environ['DISPLAY'] = ":0"
        try:
            line = subprocess.check_output(
                [self.ati_config_path,
                 "--adapter=" + str(gpuid),
                 "--odgt"])
            m = re.search('Temperature - (\d+\.\d+)\s*C', line)
            if m is None:
                return None

            return float(m.group(1))
        except OSError:
            return None

    def get_gpus(self):
        """
        Try to get the list of all available GPUs
        """
        os.environ['DISPLAY'] = ":0"
        try:
            out = subprocess.check_output([self.ati_config_path, "--list-adapters"])
            card = 0
            gpu = 0
            lines = split(out, "\n")
            for line in lines:
                r = re.search('^[ \*]+(\d+)\. [\d:\.]+ (.+)$', line)
                if r is not None:
                    yield dict(gpuid=int(r.group(1)), desc=r.group(2))
        except OSError, e:
            logger.error("aticonfig is not available at " + self.ati_config_path)
            logger.exception(e)

    def get_gpus_temp(self):
        """
        Return data formatted for the API
        """
        gpus = []
        for gpu in self.get_gpus():
            temp = self.get_gpu_temp(gpu["gpuid"])
            if temp is not None:
                gpus.append(dict(name=gpu["desc"], data=dict(temp=temp)))
            else:
                logger.warning("No temp for " + gpu["desc"] + "GPU")
        return gpus

    def get_all(self):
        return dict(custom=self.get_gpus_temp())
