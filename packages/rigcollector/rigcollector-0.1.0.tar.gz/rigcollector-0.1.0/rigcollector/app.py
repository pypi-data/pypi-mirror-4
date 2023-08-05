import aaargh
import logging
import os
import sys
import time

from rigcollector.collector import send_data

API_URL = "https://rigsmonitoring.com/api/v1"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = aaargh.App(description="Gather system metrics and send it to RigsMonitoring.com API.")

@app.cmd
@app.cmd_arg('-d', '--detach', type=str, default="0", help="Detach script to background")
@app.cmd_arg('--api-key', type=str, default="", help="Rig API Key")
@app.cmd_arg('-c', '--config_file', type=str, default="rigcollector.yml", help="YAML Config file")
@app.cmd_arg('-l', '--log-file', type=str, default="", help="Enable logging to file")
def collect(detach, api_key, config_file, log_file):

    detach_mode = int(detach)
    if detach_mode:
        logging.info("Detaching script to background")
        if os.fork():
            sys.exit()
    
    lh = None
    if log_file or detach_mode:          
        lh = logging.FileHandler(log_file if log_file else "rigcollector.log")
    else:
        lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter("%(asctime)s;%(name)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(lh)

    while 1:
        try:
            out = send_data(API_URL, api_key, config_file)

            logger.info("Sending data:")
            logger.info(out["data"])
            logger.info(out["status"])
            
            logger.info("Sleeping for " + str(out["ttw"]) + " seconds")
            time.sleep(out.get("ttw"))
        
        except Exception, e:
            logger.exception(e)

@app.cmd
@app.cmd_arg('-c', '--config_file', type=str, default="rigcollector.yml", help="YAML Config file")
def test(config_file):
    lh = logging.StreamHandler()
    lh.setFormatter(logging.Formatter("%(asctime)s;%(name)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(lh)

    out = send_data(None, None, config_file, test_mode=True)

    logger.info("Test data:")
    logger.info(out["data"])
    

def main():
    app.run()

if __name__ == '__main__':
    main()
