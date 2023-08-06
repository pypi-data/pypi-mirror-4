import sys
import os
import glob

from setuptools import setup
from setuptools import find_packages


if sys.version_info < (2, 6):
    print "blackhole requires Python 2.6 or greater"
    sys.exit(1)


version = __import__('blackhole').__version__

setup(name='blackhole',
      version=version,
      url='http://blackhole.io/',
      author="Kura",
      author_email="kura@kura.io",
      maintainer="Kura",
      maintainer_email="kura@kura.io",
      description="Tornado powered MTA for accepting all incoming emails without any disk I/O, although no messages actually ever get delivered. Mainly for testing huge send rates, for making sure developers don't accidentally send emails to real users, email integration testing and things like that.",
      long_description=open("README.rst").read(),
      license=open("LICENSE").read(),
      platforms=['linux'],
      packages=find_packages(exclude=["*.tests"]),
      install_requires=[
          'tornado==3.0',
          'setproctitle==1.1.7',
          'deiman==0.1.3',
      ],
      scripts=[
          'blackhole/bin/blackhole',
      ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet',
          'Topic :: Utilities',
          'Topic :: Communications :: Email',
          'Topic :: Communications :: Email :: Mail Transport Agents',
          'Topic :: Communications :: Email :: Post-Office',
          'Topic :: Software Development :: Testing',
          'Topic :: Software Development :: Testing :: Traffic Generation',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
      ],
      zip_safe=True,
      )
