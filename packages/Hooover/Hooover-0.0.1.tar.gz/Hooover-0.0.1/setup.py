try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='Hooover',
      version='0.0.1',
      description="Library for logging to Loggly from within Python webapps",
      author="Hoover: Mike Blume, Hooover: Justin Wilson",
      author_email="juztinwilzon@gmail.com",
      url="https://bitbucket.org/juztin/hooover",
      packages=['hooover'],
      install_requires=['requests'],
)
