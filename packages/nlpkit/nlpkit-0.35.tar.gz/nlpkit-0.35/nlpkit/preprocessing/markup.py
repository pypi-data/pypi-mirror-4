import logging
import re
from lxml import html, etree
from lxml.html.clean import Cleaner

def strip_html(text, fallback=True, drop_tags=[], keep_tags=[]):
    try:
        cleaner = Cleaner(kill_tags=drop_tags, )
        broken_html = "<html><head><title>test<body><h1>page title</h3>"

        doc = html.fragment_fromstring(broken_html, create_parent=True)
        stripped = html.fromstring(text).text_content()


#>>> parser = etree.HTMLParser()
#>>> tree   = etree.parse(StringIO(broken_html), parser)
#
#>>> result = etree.tostring(tree.getroot(),
#    ...                         pretty_print=True, method="html")
#>>> print(result)
#<html>



    except etree.XMLSyntaxError as e:
        if fallback:
            logging.debug("XML parsing failed for '{}...'. Using regexp".format(text[0:200]))
            stripped = re.sub('<[^<]+?>', '', text)
        else:
            raise e
    except etree.ParserError:
        return ''

    return stripped

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_sent = "<h1>A prestigious award<h1> Does <code>a = b**2 + c**2</code> make sense to you?"
    print strip_html("<html><head><title>test<body><h1>page title</h3>")
    print strip_html(test_sent, drop_tags=['code'])