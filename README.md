# server
Sometimes, you just need to serve some static content from a directory. When that happens, `python -m SimpleHTTPServer` or `php -S` is pretty handy, but what if you want a little more?

This script will handle all of those, but it will also allow you to minify LESS/SASS/SCSS and run Python scripts.

## Installation

1. Install the dependencies: `pip install flask libsass lesscpy` (may require `sudo`)
2. Clone the repo: `git clone https://github.com/rnelson/server.git`
3. Create a symlink: `ln -s /path/to/server/server.py ~/bin/server`

## Usage

Whatever directory you are in when you run the script is the root. This is now available at [http://localhost:9000](http://localhost:9000).

For LESS/SASS/SCSS files, give them the appropriate extension (`.less`, `.sass`, `.scss`) and they'll automatically be minified.

The Python script support relies on `globals()` to pass data from the executing script back to `server`. Two values are read, `output` and `output_type` (the latter defaults to `text/html`) to determine what to display and how to display it. The following is a trivial example:

```
#! env python

content = 'Hello, {}!'.format('World')
globals()['output'] = content
globals()['output_type'] = 'text/plain'  # defaults to 'text/html'

```

## License

Released under the [MIT License](http://rnelson.mit-license.org).
