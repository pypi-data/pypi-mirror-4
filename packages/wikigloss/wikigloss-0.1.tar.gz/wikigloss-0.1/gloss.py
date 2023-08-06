#! /usr/bin/python
import argparse
import collections
import json
import re
import urllib2

import bs4
import html2text
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters

class Glossary():
    ''' Glossary of wikipedia terms, stored in definitions OrderedDict'''
    def __init__(self, term, verbosity=1, max_terms=500):
        self.max_terms = max_terms - 1
        self.verbosity = verbosity
        self.title = self.resolve_title(term)
        self.url = "http://en.wikipedia.org/wiki/{}".format(self.title)
        self.definitions = collections.OrderedDict([ # First definition is always of term
            (self.url, {
                'title' : self.title,
                'definition' : self.get_definition(self.url)
            })
        ])
        if self.max_terms > 0:
            for title, url in self.get_links().iteritems():
                self.definitions[url] = {
                    'title': title,
                    'definition': self.get_definition(url) if self.verbosity > 0 else None,
                }

    def resolve_title(self, term):
        '''Given an input term, attempts to return a valid Wikipedia article title.'''
        term = term.strip()
        # Try extracting title from wikipedia URL
        if (re.findall(r'/wiki/(\w+)', term)):
            term = re.search(r'/wiki/(\w+)', term)
        # Scrub term through wikipedia search
        url = "http://en.wikipedia.org/w/api.php?action=query&format=json&titles={}".format(term)
        pages = json.load(urllib2.urlopen(url))['query']['pages']
        page_id = pages.keys()[0]
        if int(page_id) > 0:
            return pages[page_id]['title']
        else:
            url = "http://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&srprop=timestamp&format=json".format(term)
            results = json.load(urllib2.urlopen(url))['query']
            if results['search']:
                return results['search'][0]['title']
            try:
                return self.resolve_title(results['searchinfo']['suggestion'])
            except KeyError:
                print "Wikipedia could not find an article matching `{}`.".format(term)
                exit(1)

    def bs_filter(self, tag):
        '''BeautifulSoup selection filter to help select main article paragraph'''
        return (tag.name == 'p' and tag.parent.name == 'div' and tag.parent['id'] == 'mw-content-text')

    def get_definition(self, url):
        '''Given a wikipedia URL, extract a plain text definition using BeautifulSoup, html2text, nltk.'''
        request = urllib2.Request(url, headers={'User-Agent' : 'Browser'}) # because Wikipedia blocks Python
        soup = bs4.BeautifulSoup(urllib2.urlopen(request))
        article_html = str(soup.find(self.bs_filter))

        h = html2text.HTML2Text()
        h.body_width = 0 # no line wrapping
        h.ignore_links = True
        h.ignore_emphasis = True
        h.ignore_images = True
        article_text = h.handle(article_html.decode('utf-8'))

        punkt_param = PunktParameters()
        punkt_param.abbrev_types = set(['dr', 'vs', 'mr', 'mrs', 'prof', 'inc', 'pron'])
        sentence_splitter = PunktSentenceTokenizer(punkt_param)
        article_sentences = sentence_splitter.tokenize(article_text)
        sentences_string = ' '.join(article_sentences[:self.verbosity])
        return re.sub('\[\d*\]', '', sentences_string).strip() # remove references like [2][3], and trailing whitespace

    def get_links(self, limit=500):
        '''Given a valid Wikipedia article title, return a dictionary of limit links of the form {title : url}'''
        url = "http://en.wikipedia.org/w/api.php?action=query&format=json&titles={title}&generator=links&prop=info&inprop=url&gpllimit={limit}".format(title=self.title, limit=self.max_terms)
        raw_links = json.load(urllib2.urlopen(url))['query']['pages']
        links = {}
        for page_id, values in raw_links.iteritems():
            if int(page_id) > 0:
                links[values['title']] = values['fullurl']
        return links

    def get_html(self):
        '''Return an html string of all definitions. Sets encoding to UTF-8 for best compatability with en.wikipedia.org'''
        html = u"<html>\n<head>\n\t<meta charset='UTF-8' />\n<title>{}</title>\n</head>\n<body>\n\t<dl>".format(self.title)
        for url, value in self.definitions.iteritems():
            html += u"\n\t\t<dt><a href='{url}'>{title}</a></dt>\n\t\t\t<dd>{definition}</dd>\n".format(title=value['title'], url=url, definition=value['definition'])
        html += u'\n\t</dl>'
        html += u'\n</body>\n</html>'
        return html.encode('utf-8')

    def get_json(self):
        '''Returns a json string of all definitions.'''
        return json.dumps(self.definitions, indent=4)

    def serialize(self, data, format, filename=None):
        '''Writes data to a file.'''
        if not filename:
            filename = "{}.{}".format(self.title, format)
        with open(filename, 'wb') as f:
            f.write(data)
        print "Wrote {n} definitions to {filename}".format(n=len(self.definitions), filename=filename)

    def __str__(self):
        s = u"\n{title}\n\t{url}\n\t{definition}".format(title=self.title, url=self.url, definition=self.definition)
        if self.definitions:
            s += u'\n----------'
            for url, value in self.definitions.iteritems():
                s += u"\n{title}\n\t{url}\n\t{definition}".format(title=value['title'], url=url, definition=value['definition'])
        return s.encode('utf-8')

def main():
    formats = ['html', 'json']
    parser = argparse.ArgumentParser(description='Generate a glossary of terms from links on a Wikipedia page.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('term', help='Search term. Can be a Wikipedia URL, title of an article, or approximate search term.')
    parser.add_argument('-v', '--verbosity', default=1, type=int, metavar='LVL', help='Verbosity level; number of sentences to include in each definition.')
    parser.add_argument('-t', '--max_terms', default=10, type=int, metavar='NUM', help='Maximum number of terms to define.')
    parser.add_argument('-f', '--format', default='json', help="Output format. Valid choices are: {}".format(formats))
    parser.add_argument('-s', '--serialize', action='store_true', help='Serializes to a file, automatically named by term. If you want a custom-named file, use OS redirection instead.')
    args = parser.parse_args()

    if args.format not in formats:
        parser.error("Invalid format provided. Use one of {}".format(' '.join(formats)))

    glossary = Glossary(args.term, verbosity=args.verbosity, max_terms=args.max_terms)

    if args.format == 'html':
        data = glossary.get_html()
    else:
        data = glossary.get_json()

    if args.serialize:
        glossary.serialize(data, args.format)
    else:
        print data

if __name__ == '__main__':
    main()