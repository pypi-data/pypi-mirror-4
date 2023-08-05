import codecs
from setuptools import setup

long_description = codecs.open('README.rst', 'r', 'utf-8').read()

setup(
    name="m3u8",
    author='Globo.com',
    version="0.1.3",
    zip_safe=False,
    packages=["m3u8"],
    url="https://github.com/globocom/m3u8",
    description="Python m3u8 parser",
    long_description=long_description
    )
