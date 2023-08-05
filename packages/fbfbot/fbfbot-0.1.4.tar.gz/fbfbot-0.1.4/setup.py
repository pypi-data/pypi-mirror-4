#!/usr/bin/env python3
#
#

target = "fbf" # BHJTW change this to /var/cache/fbf on debian

import os
import sys

if sys.version_info.major < 3: print("you need to run this python3 distribute_setup.py first") ; os._exit(1)

try: 
    from setuptools import setup
except: print("i need setuptools to properly install FBFBOT") ; os._exit(1)
upload = []


try:
    from distribute_setup import use_setuptools
    use_setuptools()
except: print("you need to run this python3 distribute_setup.py first: %s" % str(ex)) ; os._exit(1)


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
    name='fbfbot',
    version='0.1.4',
    url='https://github.com/feedbackflow/fbfbot',
    author='FeedBack Flow',
    author_email='feedbackflow@gmail.com',
    description='The FeedBackFlow bot',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    scripts=['bin/fbf',
             'bin/fbf-fleet',
             'bin/fbf-irc',
             'bin/fbf-sleek',
             'bin/fbf-tornado',
            ],
    packages=['fbf',
              'fbf.db',
              'fbf.api',
              'fbf.tornado',
              'fbf.drivers',
              'fbf.drivers.console',
              'fbf.drivers.irc',
              'fbf.drivers.sleek',
              'fbf.drivers.tornado',
              'fbf.lib', 
              'fbf.utils',
              'fbf.plugs',
              'fbf.plugs.db',
              'fbf.plugs.core',
              'fbf.plugs.extra',
              'fbf.contrib',
              'fbf.contrib.natural',
              'fbf.contrib.natural.templatetags',
              'fbf.contrib.bs4',
              'fbf.contrib.bs4.builder',
              'fbf.contrib.tornado',
              'fbf.contrib.tornado.platform',
              'fbf/contrib/sleekxmpp',
              'fbf/contrib/sleekxmpp/stanza',   
              'fbf/contrib/sleekxmpp/test',     
              'fbf/contrib/sleekxmpp/roster',   
              'fbf/contrib/sleekxmpp/xmlstream',
              'fbf/contrib/sleekxmpp/xmlstream/matcher',
              'fbf/contrib/sleekxmpp/xmlstream/handler',
              'fbf/contrib/sleekxmpp/plugins',
              'fbf/contrib/sleekxmpp/plugins/xep_0004',
              'fbf/contrib/sleekxmpp/plugins/xep_0004/stanza',
              'fbf/contrib/sleekxmpp/plugins/xep_0009',
              'fbf/contrib/sleekxmpp/plugins/xep_0009/stanza',
              'fbf/contrib/sleekxmpp/plugins/xep_0030',
              'fbf/contrib/sleekxmpp/plugins/xep_0030/stanza',
              'fbf/contrib/sleekxmpp/plugins/xep_0050',
              'fbf/contrib/sleekxmpp/plugins/xep_0059',
              'fbf/contrib/sleekxmpp/plugins/xep_0060',
              'fbf/contrib/sleekxmpp/plugins/xep_0060/stanza',
              'fbf/contrib/sleekxmpp/plugins/xep_0066',
              'fbf/contrib/sleekxmpp/plugins/xep_0078',
              'fbf/contrib/sleekxmpp/plugins/xep_0085',
              'fbf/contrib/sleekxmpp/plugins/xep_0086',
              'fbf/contrib/sleekxmpp/plugins/xep_0092',
              'fbf/contrib/sleekxmpp/plugins/xep_0128',
              'fbf/contrib/sleekxmpp/plugins/xep_0199',
              'fbf/contrib/sleekxmpp/plugins/xep_0202',
              'fbf/contrib/sleekxmpp/plugins/xep_0203',
              'fbf/contrib/sleekxmpp/plugins/xep_0224',
              'fbf/contrib/sleekxmpp/plugins/xep_0249',
              'fbf/contrib/sleekxmpp/features',
              'fbf/contrib/sleekxmpp/features/feature_mechanisms',
              'fbf/contrib/sleekxmpp/features/feature_mechanisms/stanza',
              'fbf/contrib/sleekxmpp/features/feature_starttls',
              'fbf/contrib/sleekxmpp/features/feature_bind',   
              'fbf/contrib/sleekxmpp/features/feature_session',
              'fbf/contrib/sleekxmpp/thirdparty',
              'fbf/contrib/sleekxmpp/thirdparty/suelta',
              'fbf/contrib/sleekxmpp/thirdparty/suelta/mechanisms',
           ],
    long_description = """ The FeedBackFlow Bot -  https://github.com/feedbackflow/fbfbot """,
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
    data_files=[(target + os.sep + 'data', uploadfiles('fbf' + os.sep + 'data')),
                (target + os.sep + 'data' + os.sep + 'static', uploadlist('fbf' + os.sep + 'data' + os.sep + 'static')),
                (target + os.sep + 'data' + os.sep + 'templates', uploadlist('fbf' + os.sep + 'data' + os.sep + 'templates'))],
)
