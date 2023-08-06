import os.path
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

README_PATH = os.path.join(HERE, 'README.rst')
try:
    README = open(README_PATH).read()
except IOError:
    README = ''

REQUIRES=open(os.path.join(HERE, "requirements.txt")).readlines()


setup(
  name='trivio',
  packages=find_packages(),
  version='0.2.0',
  description='triv.io command line client',
  long_description=README,
  author='Scott Robertson',
  author_email='scott@triv.io',
  url='http://github.com/trivio/trivio.client',
  classifiers=[
      "Programming Language :: Python",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
      "Development Status :: 3 - Alpha",
      "Environment :: Web Environment",
      "Intended Audience :: Developers",
      "Topic :: Software Development",
  ],
  entry_points = {
    'console_scripts': [
      'trivio = triv.io.client:main',
    ]
  },
  install_requires=REQUIRES
)
