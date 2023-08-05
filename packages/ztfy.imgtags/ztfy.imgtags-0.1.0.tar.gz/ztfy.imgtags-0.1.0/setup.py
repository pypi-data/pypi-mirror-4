from setuptools import setup, find_packages
import os

DOCS = os.path.join(os.path.dirname(__file__),
                    'docs')

README = os.path.join(DOCS, 'README.txt')
HISTORY = os.path.join(DOCS, 'HISTORY.txt')
CONTRIBS = os.path.join(DOCS, 'CONTRIBUTORS.txt')

version = '0.1.0'
long_description = open(README).read() + '\n\n' + \
                   open(CONTRIBS).read() + '\n\n' + \
                   open(HISTORY).read()

tests_require = [
    'zope.testing',
]

setup(name='ztfy.imgtags',
      version=version,
      description="ZTFY package for EXIF/IPTC/XMP tags management",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='ZTFY EXIF IPTC XMP',
      author='Thierry Florac',
      author_email='tflorac@ulthar.net',
      url='http://hg.ztfy.org/ztfy.imgtags',
      license='zpl',
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
          'zc.catalog',
          'zope.app.file',
          'zope.component',
          'zope.i18nmessageid',
          'zope.interface',
          'ztfy.skin',
          'ztfy.utils',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """)
