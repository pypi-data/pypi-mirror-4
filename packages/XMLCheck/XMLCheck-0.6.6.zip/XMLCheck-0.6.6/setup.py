from distutils.core import setup

setup(name="XMLCheck",
    version="0.6.6",
    author = 'Joshua R. English',
    author_email = 'Joshua.R.English@gmail.com',
    url = 'https://code.google.com/p/pyxmlcheck/',
    packages=['xcheck'],
    description = 'xml-data validator tool',
    long_description = '''XMLCheck defines and validates XML-Data.
    Based on the elementtree interface.
    XMLCheck can create dictionaries and wrap object interfaces around
    XML-Data nodes.
    ''',
    classifiers = [
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Database',
        'Topic :: Text Processing :: Markup :: XML'
    ],
    )