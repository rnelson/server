#! env python
from __future__ import print_function, unicode_literals
from flask import Flask, Response, request, jsonify
from mimetypes import guess_type
from os.path import isfile
import sys
import sass
import lesscpy

app = Flask(__name__)
app.debug = True

INDEX_FILES = ['index.html', 'index.htm']


class Helpers:
    @staticmethod
    def returncontent(filename):
        """
        Loads a file from disk and returns the contents
        """
        f = open(filename, 'rb')
        content = f.read()
        f.close()

        return content

    @staticmethod
    def gettype(path):
        """
        Attempts to get the correct MIME type for a file,
        otherwise returns 'text/html'
        """
        (mimetype, encoding) = guess_type(path)

        if mimetype is None:
            return 'text/html'
        else:
            return mimetype

    @staticmethod
    def fourohfour(path):
        """
        Returns a simple 404 page
        """
        html = '<html><head><title>404: {}</title></head>'.format(path)
        html += '<body><h1>File Not Found</h1><p>The requested resource, '
        html += '<kbd>{}</kbd>, does not exist.</body></html>'.format(path)

        return html

    @staticmethod
    def fiveohoh(path, message=None):
        """
        Returns a simple 500 page
        """
        html = '<html><head><title>500: {}</title></head>'.format(path)
        html += '<body><h1>Internal Server Error</h1><p>The server '
        html += 'encountered an error loading <kbd>{}</kbd>.'.format(path)
        html += 'Sorry!</body></html>'

        if message is not None:
            print(message, file=sys.stderr)

        return html


@app.route('/')
def index():
    for f in INDEX_FILES:
        if isfile(f):
            return Helpers.returncontent(f)
    else:
        html = '<html><head><title>server</title></head>'
        html += '<body><h1>Welcome to server</h1><p>Place a '
        html += '<kbd>index.html</kbd> or <kbd>index.html</kbd> '
        html += 'file here to automatically load.</body></html>'

        return html


@app.route('/<path:path>')
def catch_all(path):
    # Verify the file exists, then send it to the client
    if not isfile(path):
        return (Helpers.fourohfour(path), 404)
    else:
        # Let's be adventurous: just run Python! The script being run
        # should set output content into `globals()['output']` and, if
        # necessary, the MIME type in `globals()['output_type']`
        if path.endswith('.py'):
            gDict = {'output': None, 'output_type': 'text/html'}
            execfile(path, gDict)
            if gDict['output'] is None:
                msg = 'ERROR: globals()["output"] not set by {}'.format(path)
                return (Helpers.fiveohoh(path, msg), 500)
            else:
                return Response(gDict['output'], mimetype=gDict['output_type'])

        # Run SASS/SCSS/LESS files through the appropriate compiler
        if path.endswith('.scss') or path.endswith('.sass'):
            return sass.compile(string=Helpers.returncontent(path),
                                output_style='compressed')
        if path.endswith('.less'):
            return lesscpy.compile(Helpers.returncontent(path), minify=True)

        # For everything else, just send it
        content = Helpers.returncontent(path)
        mtype = Helpers.gettype(path)

        return Response(content, mimetype=mtype)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)
