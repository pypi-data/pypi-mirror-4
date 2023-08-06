# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from setuptools import setup, find_packages

setup(name='wallaby',
      version='0.1.1',
      url='https://github.com/FreshXOpenSource',
      author='FreshX GbR',
      author_email='wallaby@freshx.de',
      license='BSD',
      description='Wallaby is a powerful yet simple framework for building Qt-based, cross-platform applications in PyQt/PySide with a CouchDB/CouchBase and Elasticsearch backend.',
      long_description=open('README.md').read(),
      package_data={'': ['LICENSE', 'AUTHORS', 'README.md']},
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
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
      packages=find_packages('.'),
      install_requires=['wallaby-app-inspector'],
      include_package_data = True
  )
