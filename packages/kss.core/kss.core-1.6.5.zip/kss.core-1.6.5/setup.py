from setuptools import setup, find_packages
import os

version = '1.6.5'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
        read('docs', 'INTRO.txt')
        + '\n' +
        'Recently changed\n'
        '================\n'
        + '\n' +
        read('docs', 'NEWS.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        read('kss/core/kukit/CHANGES.txt')
        + '\n' +
        'Download\n' +
        '========\n')

setup(name='kss.core',
      version=version,
      description="KSS (Kinetic Style Sheets) core framework",
      long_description=long_description,
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='KSS Project',
      author_email='kss-devel@codespeak.net',
      url='http://kssproject.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['kss'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.browserpage',
          'zope.browserresource',
          'zope.component',
          'zope.configuration',
          'zope.contenttype',
          'zope.datetime',
          'zope.event',
          'zope.interface',
          'zope.lifecycleevent',
          'zope.location',
          'zope.pagetemplate',
          'zope.publisher',
          'zope.schema',
          'zope.security',
          'zope.site',
          'zope.testing',
          'zope.traversing',
          # 'Zope2',
      ],
      )
