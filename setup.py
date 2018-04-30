# -*- coding: utf-8 -*-
from distutils.core import setup

_VERSION = '0.1.0'

setup(name='bottisota',
      version=_VERSION,
      description='Program battle bot AIs and let them fight against each other.',
      author='Tuomas Räsänen',
      author_email='tuomasjjrasanen@tjjr.fi',
      url='http://tjjr.fi/sw/bottisota/',
      packages=['bottisota'],
      scripts=['bin/bottisota-arena-square-500', 'bin/bottisota', 'bin/bottisota-bot-ai-edger', 'bin/bottisota-bot-ai-diagonal'],
      license='GPLv3+',
      platforms=['Linux'],
      download_url='http://tjjr.fi/sw/bottisota/releases/bottisota-%s.tar.gz' % _VERSION,
      classifiers=[
          "Development Status :: 1 - Planning",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: POSIX :: Linux",
          "Topic :: Games/Entertainment :: Real Time Strategy",
          "Programming Language :: Python :: 3",
        ],
      long_description='Bottisota is a programming game where players program battle bot AIs.',
  )
