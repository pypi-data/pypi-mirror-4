# coding: utf-8
from setuptools import setup


setupargs = {
    'name': 'paxmusica',
    'description': 'Peace on Playlists',

#    'license': '',
    'version': '0.0.3',
    
    'packages': ['paxmusica'],

    'entry_points': {
        'console_scripts': [
            'paxmusica.play = paxmusica.cli:play',
            'paxmusica.serve = paxmusica.cli:serve',
        ],
    },

    'install_requires': [
        'flask',
        'id3reader',
    ],
    'include_package_data': True,

    'author': 'Christian Kokoska',
    'author_email': '',
    'zip_safe': False

}

if __name__ == '__main__':
    setup(**setupargs)
