import io
from os.path import dirname, join
from setuptools import setup


def get_version(relpath):
  '''Read version info from a file without importing it'''
  for line in io.open(join(dirname(__file__), relpath), encoding='cp437'):
    if '__version__' in line:
      if '"' in line:
        # __version__ = "0.9"
        return line.split('"')[1]
      elif "'" in line:
        return line.split("'")[1]


setup(
    name='fqc',
    version=get_version("fqc/__init__.py"),
    url='https://github.com/pnnl/fqc',
    license='MIT',
    author='Joe Brown',
    author_email='brwnjm@gmail.com',
    description='Extensible plotting utility geared towards sequence quality control',
    long_description='',
    packages=['fqc'],
    install_requires=[
        'pandas',
    ],
    entry_points={
          'console_scripts': [
              'fqc = fqc.fqc:main'
          ]
    },
)
