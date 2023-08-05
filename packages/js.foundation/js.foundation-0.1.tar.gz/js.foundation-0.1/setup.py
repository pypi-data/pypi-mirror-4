from setuptools import setup, find_packages


setup(name='js.foundation',
      version='0.1',
      description='Foundation Fanstatic Resource',
      keywords=['fanstatic, foundation', 'jquery'],
      author='Parker Pinette',
      author_email='parker@parkerpinette.com',
      url='https://github.com/ppinette',
      packages=find_packages(),
      namespace_packages=['js'],
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
