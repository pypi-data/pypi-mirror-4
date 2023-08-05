# tl/lib/urldata.py
#
#

""" hold data of a html page. """

## tl imports

from tl.utils.name import stripname
from tl.lib.persist import Persist, PersistCollection
from tl.lib.datadir import getdatadir

## basic imports

import os

## UrlData class

class UrlData(Persist):

    def __init__(self, url, txt=None, *args, **kwargs):
        Persist.__init__(self, getdatadir() + os.sep + "spider" + os.sep + "data" + os.sep + stripname(url), *args, **kwargs)
        self.data.url = url
        self.data.txt = txt or self.data.txt or ""

## UrlDataCollection class

def UrlDataCollection(PersistCollection):

    def __init__(self, *args, **kwargs):
        self.path = getdatadir() + os.sep + "spider" + os.sep + "data" + os.sep
        PersistCollection.__init__(self, self.path, *args, **kwargs)
