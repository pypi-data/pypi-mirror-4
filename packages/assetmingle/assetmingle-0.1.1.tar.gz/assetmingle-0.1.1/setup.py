from setuptools import setup, find_packages

setup(
    name = 'assetmingle',

    packages = find_packages(),

    entry_points = {
        'console_scripts': [
            'assetmingle = assetmingle:cli_main',
        ],
    },

    include_package_data = False,

    version = '0.1.1',
    
    description = 'Convert image and file references in HTML and CSS files to data URLs',
    long_description = open('README.md').read() + open('LICENSE').read(),

    author = 'Mike Douglas',
    author_email = 'michael.j.douglas@gmail.com',

    url = 'https://github.com/mike-douglas/assetmingle',
    keywords = [ 'html', 'css', 'base64', 'dataurl' ],

    install_requires = [ 'docopt==0.6.1' ],

    classifiers = [
        'Environment :: Console',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Filters',
        'Topic :: Utilities',
        'Programming Language :: Python',
    ],
)