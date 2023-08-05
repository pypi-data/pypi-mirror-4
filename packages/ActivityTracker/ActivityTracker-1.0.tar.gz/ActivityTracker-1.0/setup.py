from setuptools import setup

setup(name='ActivityTracker',
      version='1.0',
      description='Task and time logging',
      long_description=open('README.rst').read() \
          + '\n\n' + open('CHANGES.rst').read(),
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://pypi.python.org/pypi/ActivityTracker',
      entry_points={
          'console_scripts': [
              'activitytracker = activitytracker.cli:main',
              ]},
      )
