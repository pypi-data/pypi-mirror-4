from xml.parsers.expat import ParserCreate
import re


def parse(data):
    def start_el(name, attrs):
        ParsedXML['start'][name] = attrs

    def char_handler(data):
        patt = re.compile('\S+', re.UNICODE)
        if patt.search(data):
            ParsedXML['data'].append(data)

    ParsedXML = {'start': {}, 'end': [], 'data': []}
    parser = ParserCreate()
    parser.StartElementHandler = start_el
    parser.CharacterDataHandler = char_handler
    parser.Parse(data)
    return ParsedXML


def hasURL(xml, url):
    parsed_sitemap = parse(xml)
    data = parsed_sitemap['data']
    return url in data
