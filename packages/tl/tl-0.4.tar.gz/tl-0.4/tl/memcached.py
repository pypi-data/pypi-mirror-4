# tl/memcached.py
#
#

""" memcached support functions. """

## tl imports

from tl.lib.datadir import getdatadir
#from tl.lib.config import getmainconfig

## basic imports

import os
import os.path
import logging
import time

mc = None

def isactive(path):
    stats = None
    if not mc: mcboot()
    if mc: stats = mc.get_stats()
    if stats: return stats
    return False

def mcboot():
    #if not getmainconfig().memcached: return
    logging.warn("memcached is enabled")
    try:
        import tl.contrib.memcache as memcache
        rundir = getdatadir() + os.sep + 'run'
        sock = os.path.abspath(rundir + os.sep + "memcached.socket")
        global mc
        mc = memcache.Client(["unix:%s" % sock], debug=0)
        return isactive(sock)
    except ImportError as ex: logging.warn("using builtin cache - %s" % str(ex))
    except Exception as ex: logging.warn("error starting memcached client: %s" % str(ex))

def getmc():
    #if not getmainconfig().memcached: return
    logging.warn("memcached is enabled")
    global mc
    if mc: return mc
    else:
        startmcdaemon()
        if mcboot(): return mc

def startmcdaemon():
    #if not getmainconfig().memcached: return
    logging.warn("starting memcached daemon")
    try:
        from tl.utils.popen import gozerpopen
        rundir = getdatadir() + os.sep + 'run'
        sock = os.path.abspath(rundir + os.sep + "memcached.socket")
        logging.warn("using unix socket %s" % sock)
        pidfile = sock[:-7] + ".pid"
        if os.path.exists(sock) and isactive(sock): logging.warn("memcached daemon is already running") ; return
        args = [[]]*4
        args[0] = "memcached"
        args[1] = "-s%s" % sock
        args[2] = "-P%s" % pidfile
        args[3] = "-d"
        logging.debug("running %s" % " ".join(args))
        proces = gozerpopen(args)
    except Exception as ex:
        if "No such file" in str(ex): logging.warn("no memcached installed") 
        else: logging.error('error running popen: %s' % str(ex))
        return
    data = proces.fromchild.readlines()
    returncode = proces.close()
    if returncode == 0: logging.warn("memcached started")
    else: logging.warn("can't start memcached (%s)" % returncode)

def killmcdaemon():
    #if not getmainconfig().memcached: return
    logging.warn("killing memcached daemon")
    rundir = getdatadir() + os.sep + 'run'
    sock = os.path.abspath(rundir + os.sep + "memcached.socket")
    pidfile = sock[:-7] + ".pid"
    try: pid = int(open(pidfile, "r").read().strip())
    except Exception as ex : logging.warn("can't determine pid of memcached from %s - %s" % (pidfile,str(ex))) ; return False
    logging.warn("pid is %s" % pid)
    data = isactive(sock)
    if not data: logging.warn("memcached is not runniing") ; return False
    try: curr_connections = int(data[0][1]["curr_connections"])
    except Exception as ex: logging.warn("can't determine current connections of memcached .. not killing - %s" % str(ex)) ; return False
    if curr_connections and curr_connections != 1: logging.warn("current connections of memcached is %s .. not killing" % curr_connections) ; return False
    try: os.kill(pid, 15) ; logging.warn("killed memcached with pid %s" % pid)
    except Exception as ex: logging.warn("failed to kill memcached (%s) - %s" % (pid, str(ex)))
    try: os.remove(pidfile)
    except: pass
    