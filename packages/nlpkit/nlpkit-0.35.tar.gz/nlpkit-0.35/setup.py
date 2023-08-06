from distutils.core import setup

setup(name="nlpkit",
    version="0.35",
    package_dir={'nlpkit': 'nlpkit',
                 'nlpkit.test': 'test'},
    packages=['nlpkit', 'nlpkit.wordnet', 'nlpkit.parse', 'nlpkit.preprocessing'],
    scripts=['bin/corenlp-tag.py',
             'bin/mate-parse.py'],
    author='Anders Johannsen',
    author_email='anders@johannsen.com',
    maintainer='Anders Johannsen',
    maintainer_email='anders@johannsen.com',
    url='http://pypi.python.org/pypi/nlpkit/',
    description='A collection of scripts for NLP-related command line tasks',
    install_requires=[
        "pymongo >= 2.2.0",
        ],

)
