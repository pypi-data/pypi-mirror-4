# -*- coding: utf-8 -*-
import os
import sys
from distutils.core import setup

from dev_appserver import fix_sys_path

saved_path = list(sys.path)
fix_sys_path() # wipes out sys.path
sys.path.extend(saved_path) # put back our original paths

import simpleauth

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='simpleauth',
      version=simpleauth.__version__,
      author='Alex Vagin (http://alex.cloudware.it)',
      author_email='alex@cloudware.it',
      url='http://code.google.com/p/gae-simpleauth',
      download_url='http://code.google.com/p/gae-simpleauth/source/checkout',
      description='A simple auth handler for Google App Engine supporting '
                  'OAuth 1.0a, 2.0 and OpenID',
      keywords='oauth oauth2 openid appengine google',
      platforms=["any"],
      license='MIT',
      requires=['oauth2', 'httplib2'],
      extras_require={
        'LinkedIn': ['lxml']
      },
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries',    
      ],
      packages=['simpleauth'],
      long_description=read('README')
)
