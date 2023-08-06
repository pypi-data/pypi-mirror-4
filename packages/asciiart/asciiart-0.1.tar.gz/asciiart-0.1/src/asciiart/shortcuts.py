'''
Created on 12-03-2013

@author: karol
'''

import StringIO

from PIL import Image

import requests

def create_parser(klass, image, **kwargs):
    return klass(image, **kwargs)

def image_from_file(f):
    return Image.open(f)

def image_from_url(url):
    response = requests.get(url)
    return Image.open(StringIO.StringIO(response.content))