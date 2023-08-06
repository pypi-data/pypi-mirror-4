# coding: utf-8
from setuptools import setup


setupargs = {
    'name': 'paxmusica',
    'description': 'Peace on Playlists',

#    'license': '',
    'version': '0.0.2',
    
    'packages': ['paxmusica'],

    'install_requires': [
        'flask',
        'id3reader',
    ],

    'author': 'Christian Kokoska',
    'author_email': '',
}

if __name__ == '__main__':
    setup(**setupargs)
