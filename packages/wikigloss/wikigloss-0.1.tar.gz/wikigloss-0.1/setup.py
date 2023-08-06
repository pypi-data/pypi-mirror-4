import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup

setup(
    name = 'wikigloss',
    version = '0.1',
    scripts = ['distribute_setup.py', 'gloss.py'],
    install_requires = ['beautifulsoup4==4.1.3','html2text==3.200.3', 'nltk==2.0.4'],

    #PyPI metadata
    author = "Eric Gustavson",
    author_email = "gustavson.eric@gmail.com",
    description = "Wikipedia glossary generator",
    keywords = "wikipedia glossary nlp",
    url = "http://ericg.us",
)

