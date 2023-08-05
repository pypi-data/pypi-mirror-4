import psutil
import os
import time
import yaml
import codecs
import urllib2
import urllib
import json
import re
import logging
import platform
import importlib

logger = logging.getLogger(__name__)

INTERVAL = 1

def get_conf(config_file):
    if os.path.isfile(config_file):
        with codecs.open(config_file, "r", "utf8") as f:
            return yaml.load(f)
    logger.info("no config file found")
    return {}


def load_class(full_class_string):
    """
    dynamically load a class from a string
    
    >>> klass = load_class("module.submodule.ClassName")
    >>> klass2 = load_class("myfile.Class2")

    """
    class_data = full_class_string.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]

    module = importlib.import_module(module_path)
    # Finally, we retrieve the Class
    return getattr(module, class_str)


class Collector:
    """
    Base Collector Class, handle collector configuration
    """

    def __init__(self, conf):
        self.raw_conf = conf
        self.conf = conf.get(self.__class__.__name__, {})
        self.is_active = True

    def get_data(self):
        if self.conf.get("is_active", self.is_active):
            return self.get_all()
        logger.info(self.__class__.__name__ + "is disabled")
        return {}


class SystemCollector(Collector):
    """
    Get basic system metrics
     - uptime
     - cpu
     - mem
     - load avg
    """

    def get_utptime(self):
        with open('/proc/uptime', 'r') as f:
            return float(f.readline().split()[0])    

    def get_cpu(self):
        return psutil.cpu_percent(INTERVAL)

    def get_mem(self):
        data = psutil.virtmem_usage()
        return dict(percent=data.percent, used=int(data.used), total=int(data.total))

    def get_load(self):
        return list(os.getloadavg())

    def get_all(self):
        out = dict(system=dict(cpu=self.get_cpu(),
                                mem=self.get_mem()))

        if platform.system() != "Windows":
            out["system"]["load"] = self.get_load()
            out["system"]["uptime"] = self.get_utptime()
        
        return out


class DisksCollector(Collector):
    """
    Get disks usage informations
    """

    def get_all(self):
        res = []
        for p in psutil.disk_partitions():
            if not "opts" in p.__dict__ or p.opts != "cdrom":
                data = psutil.disk_usage(p.mountpoint)
                res.append(dict(name=p.mountpoint, 
                                data=dict(total=data.total, 
                                        used=data.used, 
                                        percent=data.percent)))
        return dict(disks=res)


class NetworkCollector(Collector):
    """
    Get upload/download for each network interface
    """

    def get_network_usage(self):
        """
        Return bytes_sent, bytes_recv for each interfaces
        """
        network_usage = {}
        for key, val in psutil.network_io_counters(pernic=True).items():
            if not re.findall(r"\.{.+}|loopback|\biface\b|\blo\b", key, re.IGNORECASE):
                network_usage[key] = dict(bs=val.bytes_sent, br=val.bytes_recv)
        return network_usage

    def get_all(self):
        """
        Return upload/download for 1 secondes in bytes
        for each interfaces
        """
        nu1 = self.get_network_usage()
        time.sleep(INTERVAL)
        nu2 = self.get_network_usage()

        res = []
        for iface in nu1.keys():
            upload = int(nu2[iface]["bs"] - nu1[iface]["bs"])
            download = int(nu2[iface]["br"] - nu1[iface]["br"])
            data = dict(upload=upload,
                        download=download)
            res.append(dict(name=iface, data=data))
        return dict(network=res)


class ProcessesCollector(Collector):
    """
    Get CPU/MEM usage for defined processes
    """

    def __init__(self, conf):
        Collector.__init__(self, conf)
        self.processes = self.conf.get("processes", [])

    def get_pid_by_name(self, name):
        for proc in psutil.process_iter():
            if name in (" ".join(proc.cmdline) or proc.name):
                return proc.pid
        return None 

    def get_process_infos(self, pid):
        p = psutil.Process(int(pid))
        return dict(mem="%.2f" % p.get_memory_percent(), 
                    cpu=p.get_cpu_percent(interval=INTERVAL))

    def get_all(self):
        res = []
        for process in self.processes:
            pid = self.get_pid_by_name(process)
            if pid:
                res.append(dict(name=process,
                                data=self.get_process_infos(pid)))
            else:
                logger.warning(process + " is not found")
        return dict(processes=res)


class CustomCollector(Collector):
    """
    Handle custom collectors (configuration and call)
    """

    def __init__(self, conf):
        Collector.__init__(self, conf)
        self.custom = self.conf.get("custom", [])

    def get_all(self):
        """
        Fetch all collector from config and
        extend all the data.
        """
        res = dict(custom=[])

        # Load each custom collector from config file
        for custom_collector in self.custom:
            try:
                CurrentCollector = load_class(custom_collector)
                res["custom"].extend(CurrentCollector(self.raw_conf).get_data()["custom"])
            except Exception, e:
                logger.error(custom_collector + " not found !")
                logger.exception(e)    
        return res


def send_data(api_url, api_key, config_file, test_mode=False):
    """
    Retrieve data for each collector and
    send data to the API via a POST request.
    """
    conf = get_conf(config_file)

    out = {}
    for col in [ProcessesCollector, 
                SystemCollector, 
                DisksCollector, 
                NetworkCollector,
                CustomCollector]:
        try:
            out.update(col(conf).get_data())
        except Exception, e:
            logger.exception(e)
    
    data = dict(ts=time.time(),
                data=out,
                api_key=api_key)
    
    if test_mode:
        return dict(data=data)

    req = urllib2.Request(conf.get("api_url", api_url),
                        json.dumps(data),
                        {'Content-Type': 'application/json'})
        
    resp = json.loads(urllib2.urlopen(req).read())
        
    return dict(status=resp["status"],
                ttw=int(resp.get("ttw", 60 * 5)),
                data=data)
