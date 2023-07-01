#! env python
from flask import Flask, Response, jsonify, make_response, request
from mimetypes import guess_type
from os.path import isfile
import sys
import sass
import lesscpy

app = Flask(__name__)
app.debug = True

INDEX_FILES = ['index.py', 'index.html', 'index.htm']


class Helpers:
    @staticmethod
    def returncontent(filename):
        """
        Loads a file from disk and returns the contents
        """
        content = ''
        with open(filename, 'rb') as f:
            content = f.read()

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

    @staticmethod
    def runpython(path):
        """
        Runs a Python script
        """
        g_dict = {'output': None, 'output_type': 'text/html'}
        exec(open(path, 'r').read(), g_dict)
        if g_dict['output'] is None:
            msg = 'ERROR: globals()["output"] not set by {}'.format(path)
            return Helpers.fiveohoh(path, msg), 500
        else:
            return Response(g_dict['output'], mimetype=g_dict['output_type'])


@app.route('/')
def index():
    for f in INDEX_FILES:
        if isfile(f):
            if f.endswith('.py'):
                return Helpers.runpython(f)
            else:
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
        return Helpers.fourohfour(path), 404
    else:
        # Let's be adventurous: just run Python! The script being run
        # should set output content into `globals()['output']` and, if
        # necessary, the MIME type in `globals()['output_type']`
        if path.endswith('.py'):
            return Helpers.runpython(path)

        # Run SASS/SCSS/LESS files through the appropriate compiler
        if path.endswith('.scss') or path.endswith('.sass'):
            content = str(Helpers.returncontent(path), 'utf-8')
            css = sass.compile(string=content, output_style='compressed')
            r = make_response(css)
            r.headers['Content-Type'] = 'text/css'
            r.headers['X-Content-Type-Options'] = 'nosniff'
            return r

        if path.endswith('.less'):
            css = lesscpy.compile(path, minify=True)
            r = make_response(css)
            r.headers['Content-Type'] = 'text/css'
            r.headers['X-Content-Type-Options'] = 'nosniff'
            return r

        # For everything else, just send it
        content = Helpers.returncontent(path)
        mtype = Helpers.gettype(path)

        return Response(content, mimetype=mtype)


if __name__ == '__main__':
    port = 9000

    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            port = 9000

    app.run(host='0.0.0.0', port=port)
