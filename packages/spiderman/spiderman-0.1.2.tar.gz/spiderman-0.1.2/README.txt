=========
Spiderman
=========

Spiderman is a wrapper around web.py to make it more like sinatra. Use it like this::

    #!env/bin/python

    from spiderman.helpers import *

    @get('/')
    def main_page():
        pass # main_page.haml in 'views' gets rendered.

    @get('/example')
    def example():
        # local vars get passed to example.haml template
        person = { 'name' : 'John', 'age' : 28 }
        return haml()
