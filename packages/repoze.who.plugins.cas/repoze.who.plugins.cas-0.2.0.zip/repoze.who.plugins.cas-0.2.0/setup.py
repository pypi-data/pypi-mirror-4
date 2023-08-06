
import os
import sys

from setuptools import setup, find_packages


version = '0.2.0'
name='repoze.who.plugins.cas'

here = os.path.abspath(os.path.dirname(__file__))

README = open(os.path.join(here, 'README.rst')).read()
INSTALL = open(os.path.join(here, 'INSTALL.rst')).read()
TODO = open(os.path.join(here, 'TODO.rst')).read()
ISSUES = open(os.path.join(here, 'ISSUES.rst')).read()
CHANGELOG = open(os.path.join(here, 'CHANGELOG.rst')).read()


setup(name=name,
      version=version,
      description='CAS plugin for repoze.who by Makina Corpus',
      long_description='\n\n'.join([README, INSTALL, TODO, ISSUES, CHANGELOG]),
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
          'Topic :: System :: Systems Administration :: Authentication/Directory'
      ],
      keywords='cas authentication server web wsgi repoze repoze.who sponsorised by Makina Corpus',
      author='Simon Thepot, Mathieu Pasquet',
      author_email='dj.coin@laposte.net, kiorky@cryptelium.net',
      #url = 'http://cheeseshop.python.org/pypi/%s' % name,
      url = 'http://github.com/kiorky/repoze.who.plugins.cas/',
      license = 'BSD',
      namespace_packages=['repoze', 'repoze.who', 'repoze.who.plugins',
                          'repoze.who.plugins.cas'],
      include_package_data=True,
      zip_safe=False,
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      install_requires=[
          'setuptools',
          'Paste',
          'repoze.who>=1.0',
      ],
      extras_require={'test': ['ipython',
                               'zope.testing',
                               'PasteDeploy',
                               ],
                     },
      )
