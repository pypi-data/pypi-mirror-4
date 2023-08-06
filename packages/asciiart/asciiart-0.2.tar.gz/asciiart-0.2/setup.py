'''
Created on 12-03-2013

@author: kamil
'''
from setuptools import setup
setup(
    name = "asciiart",
    version = "0.2",
    package_dir = {'': 'src'},
    packages = [
        'asciiart',
    ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = [
        'requests>=1.1.0',
        'Pillow>=1.7.8',
    ],

    package_data = {},

    author = "Karol Majta",
    author_email = "karol@karolmajta.com",
    description = "Just some ascii art stuff...",
    license = "JSON License",
    keywords = "asciiart",
    url = "http://asciiart.readthedocs.org/",
    
    entry_points = {
        'console_scripts': [
            'file2ascii = asciiart.commands:file2ascii',
            'url2ascii = asciiart.commands:url2ascii' 
        ],
    }
)
