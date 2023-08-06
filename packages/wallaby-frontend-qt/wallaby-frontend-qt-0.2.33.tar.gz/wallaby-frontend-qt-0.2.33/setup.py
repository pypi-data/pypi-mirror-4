# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from setuptools import setup, find_packages
import platform, sys

setup(name='wallaby-frontend-qt',
      version='0.2.33',
      url='https://github.com/FreshXOpenSource/wallaby-frontend-qt',
      author='FreshX GbR',
      author_email='wallaby@freshx.de',
      license='BSD',
      description='Integration of Qt into wallaby.',
      long_description=open('README.md').read(),
      package_data={'': ['LICENSE', 'AUTHORS', 'README.md']},
      classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
      ],
      scripts=["wlby"],
      packages=find_packages('.'),
      include_package_data = True,
      install_requires=['wallaby-base'] # and PyQt or PySide ... currently from brew/yum/apt-get
  )
