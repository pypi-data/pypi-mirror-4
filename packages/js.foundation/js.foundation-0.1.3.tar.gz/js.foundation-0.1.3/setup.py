import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()


setup(name='js.foundation',
      version='0.1.3',
      description='Foundation Fanstatic Resource',
      keywords=['fanstatic, foundation', 'jquery'],
      author='Parker Pinette',
      author_email='parker@parkerpinette.com',
      url='https://github.com/ppinette',
      packages=find_packages(),
      namespace_packages=['js'],
      include_package_data=True,
      classifiers=[
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: OS Independent',
      ],
      install_requires=[
          'fanstatic',
          'js.jquery',
          'js.jquery_cookie',
      ],
      entry_points={
          'fanstatic.libraries': [
              'foundation = js.foundation:library',
          ],
      },
      )
