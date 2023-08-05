#!/usr/bin/env python3
#
#

target = "ggz" # BHJTW change this to /var/cache/jsb on debian

import os

try: 
    from setuptools import setup
except: print("i need setuptools to properly install JSB3") ; os._exit(1)

upload = []

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir): print("%s does not exist" % dir) ; os._exit(1)
    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if not os.path.isdir(d):
            if file.endswith(".pyc"):
                continue
            upl.append(d)
    return upl

def uploadlist(dir):
    upl = []

    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if os.path.isdir(d):   
            upl.extend(uploadlist(d))
        else:
            if file.endswith(".pyc"):
                continue
            upl.append(d)

    return upl

setup(
    name='ggzbot',
    version='0.1.2',
    url='http://ggzbot.googlecode.com/',
    download_url="http://code.google.com/p/ggzbot/downloads", 
    author='Bart Thate',
    author_email='ggzpreventie@gmail.com',
    description='supporting the GGZ patients since 14-9-2012',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    scripts=['bin/ggz',
             'bin/ggz-fleet',
             'bin/ggz-irc',
             'bin/ggz-sleek',
             'bin/ggz-tornado',
            ],
    packages=['ggz',
              'ggz.db',
              'ggz.drivers',
              'ggz.drivers.console',
              'ggz.drivers.irc',
              'ggz.drivers.sleek',
              'ggz.drivers.tornado',
              'ggz.lib', 
              'ggz.utils',
              'ggz.plugs',
              'ggz.plugs.db',
              'ggz.plugs.core',
              'ggz.plugs.extra',
              'ggz.contrib',
              'ggz.contrib.bs4',
              'ggz.contrib.bs4.builder',
              'ggz.contrib.tornado',
              'ggz.contrib.tornado.platform',
              'ggz/contrib/sleekxmpp',
              'ggz/contrib/sleekxmpp/stanza',   
              'ggz/contrib/sleekxmpp/test',     
              'ggz/contrib/sleekxmpp/roster',   
              'ggz/contrib/sleekxmpp/xmlstream',
              'ggz/contrib/sleekxmpp/xmlstream/matcher',
              'ggz/contrib/sleekxmpp/xmlstream/handler',
              'ggz/contrib/sleekxmpp/plugins',
              'ggz/contrib/sleekxmpp/plugins/xep_0004',
              'ggz/contrib/sleekxmpp/plugins/xep_0004/stanza',
              'ggz/contrib/sleekxmpp/plugins/xep_0009',
              'ggz/contrib/sleekxmpp/plugins/xep_0009/stanza',
              'ggz/contrib/sleekxmpp/plugins/xep_0030',
              'ggz/contrib/sleekxmpp/plugins/xep_0030/stanza',
              'ggz/contrib/sleekxmpp/plugins/xep_0050',
              'ggz/contrib/sleekxmpp/plugins/xep_0059',
              'ggz/contrib/sleekxmpp/plugins/xep_0060',
              'ggz/contrib/sleekxmpp/plugins/xep_0060/stanza',
              'ggz/contrib/sleekxmpp/plugins/xep_0066',
              'ggz/contrib/sleekxmpp/plugins/xep_0078',
              'ggz/contrib/sleekxmpp/plugins/xep_0085',
              'ggz/contrib/sleekxmpp/plugins/xep_0086',
              'ggz/contrib/sleekxmpp/plugins/xep_0092',
              'ggz/contrib/sleekxmpp/plugins/xep_0128',
              'ggz/contrib/sleekxmpp/plugins/xep_0199',
              'ggz/contrib/sleekxmpp/plugins/xep_0202',
              'ggz/contrib/sleekxmpp/plugins/xep_0203',
              'ggz/contrib/sleekxmpp/plugins/xep_0224',
              'ggz/contrib/sleekxmpp/plugins/xep_0249',
              'ggz/contrib/sleekxmpp/features',
              'ggz/contrib/sleekxmpp/features/feature_mechanisms',
              'ggz/contrib/sleekxmpp/features/feature_mechanisms/stanza',
              'ggz/contrib/sleekxmpp/features/feature_starttls',
              'ggz/contrib/sleekxmpp/features/feature_bind',   
              'ggz/contrib/sleekxmpp/features/feature_session',
              'ggz/contrib/sleekxmpp/thirdparty',
              'ggz/contrib/sleekxmpp/thirdparty/suelta',
              'ggz/contrib/sleekxmpp/thirdparty/suelta/mechanisms',
           ],
    long_description = """ Omdat Voorkomen Beter Is - see http://ggzpreventie.nl/ggzbot """,
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
    data_files=[(target + os.sep + 'data', uploadfiles('ggz' + os.sep + 'data')),
                (target + os.sep + 'data' + os.sep + 'static', uploadlist('ggz' + os.sep + 'data' + os.sep + 'static')),
                (target + os.sep + 'data' + os.sep + 'templates', uploadlist('ggz' + os.sep + 'data' + os.sep + 'templates'))],
)
