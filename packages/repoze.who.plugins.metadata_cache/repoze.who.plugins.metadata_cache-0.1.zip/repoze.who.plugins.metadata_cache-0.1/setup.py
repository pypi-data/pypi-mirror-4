
import os
import sys

from setuptools import setup, find_packages


version = '0.1'
name='repoze.who.plugins.metadata_cache'

here = os.path.abspath(os.path.dirname(__file__))

README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

setup(name=name,
      version=version,
      description='Metadata caching plugin for repoze.who',
      long_description='\n\n'.join([README, CHANGES]),
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
      keywords='server web wsgi repoze repoze.who metadata',
      author='David Beitey',
      author_email=u'qnivq@qnivqwo.pbz'.decode('rot13'),
      url='http://github.com/davidjb/repoze.who.plugins.metadata_cache/',
      license='BSD',
      namespace_packages=['repoze',
                          'repoze.who',
                          'repoze.who.plugins',
                          'repoze.who.plugins.metadata_cache'],
      include_package_data=True,
      zip_safe=False,
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      setup_requires=[
          'setuptools',
          'setuptools-git',
      ],
      install_requires=[
          'repoze.who>=1.0',
      ],
      extras_require={'test': ['ipython',
                               'ipdb',
                               'nose',
                               ],
                     },
      )
