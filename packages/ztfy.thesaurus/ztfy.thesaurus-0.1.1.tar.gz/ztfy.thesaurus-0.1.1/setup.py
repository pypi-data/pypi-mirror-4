from setuptools import setup, find_packages
import os

DOCS = os.path.join(os.path.dirname(__file__),
                    'docs')

README = os.path.join(DOCS, 'README.txt')
HISTORY = os.path.join(DOCS, 'HISTORY.txt')
CONTRIBS = os.path.join(DOCS, 'CONTRIBUTORS.txt')

version = '0.1.1'
long_description = open(README).read() + '\n\n' + \
                   open(CONTRIBS).read() + '\n\n' + \
                   open(HISTORY).read()

tests_require = [
    'zope.testing',
]

setup(name='ztfy.thesaurus',
      version=version,
      description="ZTFY thesaurus management package",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='http://www.ztfy.org',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['ztfy'],
      include_package_data=True,
      package_data={'': ['*.zcml', '*.txt', '*.pt', '*.pot', '*.po', '*.mo', '*.png', '*.gif', '*.jpeg', '*.jpg', '*.css', '*.js']},
      zip_safe=False,
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'chardet',
          'fanstatic',
          'hurry.query',
          'lxml',
          'z3c.form',
          'z3c.formjs',
          'z3c.json',
          'z3c.jsonrpc',
          'z3c.pagelet',
          'z3c.template',
          'zc.catalog',
          'ZODB3',
          'zope.annotation',
          'zope.app.catalog',
          'zope.authentication',
          'zope.catalog',
          'zope.component',
          'zope.componentvocabulary',
          'zope.container',
          'zope.copypastemove',
          'zope.dublincore',
          'zope.i18n',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.intid',
          'zope.location',
          'zope.processlifetime',
          'zope.publisher',
          'zope.schema',
          'zope.security',
          'zope.traversing',
          'zopyx.txng3.core',
          'zopyx.txng3.ext',
          'ztfy.blog',
          'ztfy.i18n',
          'ztfy.jqueryui >= 0.6.0',
          'ztfy.security',
          'ztfy.skin >= 0.3.0',
          'ztfy.utils >= 0.3.7',
      ],
      entry_points={
          'fanstatic.libraries': [
              'ztfy.thesaurus = ztfy.thesaurus.browser:library',
          ]
      })
