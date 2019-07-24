from codecs import open as copen
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))


setup(
    name='youtube-upload',
    version='0.2.2',
    description='Python wrapper for youtube data Api video upload',
    long_description="Python wrapper for youtube data Api video upload",
    url='https://github.com/odysseusmax/youtube-upload',
    author='Christy Roys',
    author_email='royschristy@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['youtube', 'data', 'api', 'upload'],
    packages=find_packages(exclude=[]),
    install_requires=['google-api-python-client', 'oauth2client', 'httplib2'],
)

