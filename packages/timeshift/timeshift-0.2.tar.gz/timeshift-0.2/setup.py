from distutils.core import setup

with open('README.rst', 'r') as readme:
    README_TEXT = readme.read()

setup(name='timeshift',
      version='0.2',
      author='Neil Martinsen-Burrell',
      author_email='neilmartinsenburrell@gmail.com',
      url='http://bitbucket.org/nmb/timeshift',
      description='A python program for recording Internet radio streams and '
      'saving them for later listening',
      long_description=README_TEXT,
      classifiers=['Programming Language :: Python',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: End Users/Desktop',
          'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
          ],

      packages=[''],
      scripts=['timeshift.py'],

      )
