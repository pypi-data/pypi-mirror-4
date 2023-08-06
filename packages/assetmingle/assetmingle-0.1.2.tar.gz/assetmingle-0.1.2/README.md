assetmingle
===========

Easily mingle your images with your HTML/CSS!

This tool replaces image assets included in HTML and CSS files with [Data URLs][1], reducing the number of requests needed to load a page. It's useful for small images used on a page; GIFs, PNGs, small sprites, etc.

Assetmingle is designed to be part of your deployment tools keychain. It looks for assets with the '#mingle' anchor as part of their URL, which means you can happily continue to work in a development environment and just "compile" the resulting CSS when you're ready to deploy. Hooray!

[1]: http://en.wikipedia.org/wiki/Data_URI_scheme "Wikipedia Data URI Entry"

Installation
============

    pip install assetmingle

or

    python ./setup.py install

Usage
=====

Just add #mingle to the end of the URLs to the image assets in your CSS or HTML like so:

    body
    {
        background: url('/images/small_background.png#mingle');
    }

And then run:

    assetmingle main.css

Assuming the 'images' directory is in the same place as main.css is, then your CSS will be changed to:
    
    body
    {
        background: url('data:image/png;base64,iVBORw0KGgoAAA...');
    }

That's it!

Example Deployment Use
======================

I usually use assetmingle in a deployment step. I love [Fabric][2], so the following is an example of a task that I use frequently in projects where I also have some sort of deploy step:

    @task
    def mingle_css():
        local('assetmingle -o --root=app/static app/static/css/main.css > app/static/css/main.final.css')

The -o option outputs the new CSS to standard out and --root defines where the images directory lives

[2]: http://www.fabfile.org "Fabric, a simple tool for remote execution and deployment"

Documentation
=============

    Usage: assetmingle [-hvo] [--root=<path>] [INPUT ...]

    Options:
        -root=<path> The directory where your images or assets can be referenced from.
        -o           Output everything to standard out
        -h --help    Show this screen.
        -v           Be verbose.
