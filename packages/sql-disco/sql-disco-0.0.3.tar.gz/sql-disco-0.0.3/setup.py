from setuptools import setup, find_packages
setup(name='sql-disco',
  version="0.0.3",
  description='Disco SQL Connector',
  author='Jon Eisen',
  author_email='jon.m.eisen@gmail.com.com',
  url='http://www.joneisen.me',
  license='MIT Licensed',

  install_requires=[],
  packages=find_packages(".", exclude=["test"]),

  scripts = [],
  zip_safe = False

  # test_suite='sqldisco.test',
)