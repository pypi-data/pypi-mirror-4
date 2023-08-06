'''
Created on 12-03-2013

@author: kamil
'''
import sys

from asciiart import parsers, shortcuts

parsers = {
    'monochrome': parsers.BinaryParser,
    'greyscale': parsers.GreyscaleParser,
    'greyscalehtml': parsers.HtmlGreyscaleParser,
    'colorhtml': parsers.HtmlColorParser,
}

html_template = '''
    <!doctype html>
        <head>
            {0}
        </head>
        </body>
            {1}
        </body>
    </html>
    '''
    
styles = """
<style>
    pre {
        font-size: 10px;
        font-weight: bold;
        line-height: 6px;
    }
</style>
"""

def file2ascii():
    parser_name = sys.argv[1]
    inp = sys.argv[2]
    dimensions = sys.argv[3]
    output = sys.argv[4]
    
    with open(output, 'w') as fp:
        image = shortcuts.image_from_file(inp)
        parser_klass = parsers[parser_name]
        parser = parser_klass(image)
        width, height = [int(x) for x in dimensions.split("x")]
        fp.write(html_template.format(styles, parser.parse(width, height)))

def url2ascii():
    parser_name = sys.argv[1]
    url = sys.argv[2]
    dimensions = sys.argv[3]
    filename = sys.argv[4]
    
    with open(filename, 'w') as fp:
        image = shortcuts.image_from_url(url)
        parser_klass = parsers[parser_name]
        parser = parser_klass(image)
        width, height = [int(x) for x in dimensions.split("x")]
        fp.write(html_template.format(styles, parser.parse(width, height)))