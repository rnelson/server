#! env python3

with open('.template.html', 'r', encoding='utf-8') as f:
    source = f.read()
    source = source.format('Welcome to the server.py demo site!')
    globals()['output'] = source
