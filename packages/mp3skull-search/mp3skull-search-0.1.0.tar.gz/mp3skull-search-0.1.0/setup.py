#/usr/bin/python3

from distutils.core import setup

setup(
    name='mp3skull-search',
    version='0.1.0',
    description='A module to search mp3skull.com',
    author='Jeroen Pelgrims',
    author_email='jeroen.pelgrims@gmail.com',
    url='https://bitbucket.org/resurge/mp3skull-search',
    download_url='https://bitbucket.org/resurge/mp3skull-search/downloads',
    py_modules=['mp3skull'],
    requires=['beautifulsoup4'],
    provides=['mp3skull'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'Topic :: Internet'
    ]
)