import urllib2
import time
import cookielib

#urllib2 cookie support
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

#logging
import logging
logger = logging.getLogger(__name__)

network_flow_checks = {
    "getthumbinfo": { 
        "count":        0,
        "max_sleep":    0.5, #in secs
        "last_invoked": time.time(),
    },
    "getflv": { 
        "count":        0,
        "max_sleep":    1.5,
        "last_invoked": time.time(),
    },
    "mylistAPI": { 
        "count":        0,
        "max_sleep":    1.5,
        "last_invoked": time.time(),
    },
    "searchAPI": { 
        "count":        0,
        "max_sleep":    1.5,
        "last_invoked": time.time(),
    },
}

def urlopen(req, category=None, msg=None):
    logger.info("APIcall(%s): %s",category , msg)

    # sleep (only) when request speed is too high
    if category in network_flow_checks:
        interval        = time.time() - network_flow_checks[category]["last_invoked"]
        time_to_sleep   = network_flow_checks[category]["max_sleep"] - interval
        if time_to_sleep > 0:
            logger.info("NeworkI/O %s reached limit. Sleep %.2f sec."%(msg,time_to_sleep))
            time.sleep(time_to_sleep)
        network_flow_checks[category]["last_invoked"] = time.time()

    return urllib2.urlopen(req)
