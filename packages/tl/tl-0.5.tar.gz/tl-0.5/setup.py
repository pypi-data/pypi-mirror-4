#!/usr/bin/env python3
#
#

target = "tl" 

import os
import sys

if sys.version_info.major < 3: print("you need to run T I M E L I N E with python3") ; os._exit(1)

upload = []

try: 
   from setuptools import setup
except Exception as ex:
    try:
        from bootstrap.distribute_setup import use_setuptools
        use_setuptools()
    except Exception as ex:
        print(str(ex))
        print("T I M E L I N E needs the distribute package to be installed, look in the bootstrap directory if it cannot be installed system-wide")
        os._exit(1)
    try: 
       from setuptools import setup
    except Exception as ex:
        print(str(ex))
        print("T I M E L I N E needs the distribute package to be installed, look in the bootstrap directory if it cannot be installed system-wide")
        os._exit(1)

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir): print("%s does not exist" % dir) ; os._exit(1)
    for file in os.listdir(dir):
        if not file or file.startswith('.'): continue
        d = dir + os.sep + file
        if not os.path.isdir(d):
            if file.endswith(".pyc"): continue
            upl.append(d)
    return upl

def uploadlist(dir):
    upl = []
    for file in os.listdir(dir):
        if not file or file.startswith('.'): continue
        d = dir + os.sep + file
        if os.path.isdir(d): upl.extend(uploadlist(d))
        else:
            if file.endswith(".pyc"): continue
            upl.append(d)
    return upl

from tl.version import __version__

setup(
    name='tl',
    version='%s' % __version__,
    url='https://github.com.feedbackflow.tl',
    author='Bart Thate',
    author_email='feedbackflow@gmail.com',
    description='T I M E L I N E - RL events tracking software',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    requires=['distribute',],
    scripts=['bin/tl',
             'bin/tl-fleet',
             'bin/tl-irc',
             'bin/tl-xmpp',
            ],
    packages=['tl',
              'tl.db',
              'tl.drivers',
              'tl.drivers.console',
              'tl.drivers.irc',
              'tl.drivers.xmpp',
              'tl.drivers.twitter',
              'tl.utils',
              'tl.plugs',
              'tl.plugs.db',
              'tl.plugs.core',
              'tl.plugs.extra',
              'tl.plugs.timeline',
              'tl.contrib',
              'tl.contrib.bs4',
              'tl.contrib.bs4.builder',
              'tl.contrib.tweepy',
              'tl.contrib.sleekxmpp',
              'tl.contrib.sleekxmpp.stanza',   
              'tl.contrib.sleekxmpp.test',     
              'tl.contrib.sleekxmpp.roster',   
              'tl.contrib.sleekxmpp.xmlstream',
              'tl.contrib.sleekxmpp.xmlstream.matcher',
              'tl.contrib.sleekxmpp.xmlstream.handler',
              'tl.contrib.sleekxmpp.plugins',
              'tl.contrib.sleekxmpp.plugins.xep_0004',
              'tl.contrib.sleekxmpp.plugins.xep_0004.stanza',
              'tl.contrib.sleekxmpp.plugins.xep_0009',
              'tl.contrib.sleekxmpp.plugins.xep_0009.stanza',
              'tl.contrib.sleekxmpp.plugins.xep_0030',
              'tl.contrib.sleekxmpp.plugins.xep_0030.stanza',
              'tl.contrib.sleekxmpp.plugins.xep_0050',
              'tl.contrib.sleekxmpp.plugins.xep_0059',
              'tl.contrib.sleekxmpp.plugins.xep_0060',
              'tl.contrib.sleekxmpp.plugins.xep_0060.stanza',
              'tl.contrib.sleekxmpp.plugins.xep_0066',
              'tl.contrib.sleekxmpp.plugins.xep_0078',
              'tl.contrib.sleekxmpp.plugins.xep_0085',
              'tl.contrib.sleekxmpp.plugins.xep_0086',
              'tl.contrib.sleekxmpp.plugins.xep_0092',
              'tl.contrib.sleekxmpp.plugins.xep_0128',
              'tl.contrib.sleekxmpp.plugins.xep_0199',
              'tl.contrib.sleekxmpp.plugins.xep_0202',
              'tl.contrib.sleekxmpp.plugins.xep_0203',
              'tl.contrib.sleekxmpp.plugins.xep_0224',
              'tl.contrib.sleekxmpp.plugins.xep_0249',
              'tl.contrib.sleekxmpp.features',
              'tl.contrib.sleekxmpp.features.feature_mechanisms',
              'tl.contrib.sleekxmpp.features.feature_mechanisms.stanza',
              'tl.contrib.sleekxmpp.features.feature_starttls',
              'tl.contrib.sleekxmpp.features.feature_bind',   
              'tl.contrib.sleekxmpp.features.feature_session',
              'tl.contrib.sleekxmpp.thirdparty',
              'tl.contrib.sleekxmpp.thirdparty.suelta',
              'tl.contrib.sleekxmpp.thirdparty.suelta.mechanisms',
           ],
    long_description = """ 
    T I M E L I N E -  keep track of what you are doing (console, IRC, XMPP) - https://github.com/feedbackflow/tl 
    
    Ten Rules For The New World
    Kenmerk: 69389/12

    Punishment, the fruit of knowledge of good and evil, will be forbidden

    Every person, thing, existance, awareness or other entity, being or not being, can ask for a proces described below.

    The basic right is to be able to ask for help in difficult situations. Help from the outside, when fear of ending existence appears. 
    The rules below are for those who are willing to help. 
    One day these rules will be law, where nothing will be excluded from:

    1) you shall do no harm
    2) you shall judge but put no negative actions on your judgement
    3) this judgement you shall use to see what is going on
    4) with this knowledge of what is going on you will look at what the cause is
    5) when you know what the cause is you will take action to prevent further negative consequences
    6) you will do this proces in the open, controlable for everybody and thing
    7) you will evaluate how this proces works out, also in the open.
    8) You will make your judgement your own and not someone elses
    9) It is for you to bring peace on this earth and every else where this light needs to shine
    10) as last, be aware, be aware of what you think, do, cause, feel, see, hear, all that you perceive. For judgement can only be done properly if you see all the factors that influence a situation. Be aware of what makes you.     
    
    """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    data_files=[('examples', uploadfiles('examples'))],
    package_data={'': ["*.example"]},
)
