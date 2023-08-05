# -*- encoding: utf-8 -*-
from rigcollector.collector import Collector
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

HEADER_REGEXES = ["temp", "load"]

class GpuzCollector(Collector):
    """
    Retrieve data from GPU-Z (http://www.techpowerup.com/gpuz/)
    log file.
    """

    def __init__(self, conf):
        Collector.__init__(self, conf)
        self.header_regexes = self.conf.get("header_regexes", HEADER_REGEXES)
        logging.info("GPU-Z Header regexes: " + repr(self.header_regexes))
        self.log_file = self.conf.get("log_file")
        if not self.log_file:
            logger.error("No CPU-Z log file defined")
            raise Exception("No CPU-Z log file defined")
        else:
            logger.info("CPU-Z log file: " + self.log_file)

    def parse_gpuz_log(self):
        """
        Get the first line (for header) and
        the last line (for latest data) and return
        a dict based on filter regexes.
        It also check that the latest data is not too hold.
        """
        first_line = None
        for line in open(self.log_file):
            if first_line is None:
                first_line = line
            if line != "\n":
                last_line = line
        
        headers = [h.strip() for h in first_line.split(",") if h.strip()]
        latest_data = [d.strip() for d in last_line.split(",") if d.strip()]

        latest_data_dt = datetime.strptime(latest_data[0], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - latest_data_dt > timedelta(minutes=10):
            raise Exception("Latest data from GPU-Z log file is too old: " + str(latest_data_dt))

        data = {}

        combined = "(" + "|".join(self.header_regexes) + ")"
            
        for index, header in enumerate(headers):
            if re.findall(combined, header, re.IGNORECASE):
                res = latest_data[index]
                data[header.decode('mbcs', 'ignore').replace(".", "")] = float(res) if "." in res else int(res)
        
        if not data:
            logger.warning("No data found in CPU-Z log file")

        return dict(name="GPU-Z", data=data)

    def get_all(self):
        return dict(custom=[self.parse_gpuz_log()])