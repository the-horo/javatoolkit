# Copyright 2020 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

import io
import xml.sax
import xml.sax.xmlreader

def _make_parser(*, content_handler=None, dtd_handler=None, entity_resolver=None, error_handler=None, locale=None, features=None, properties=None):
    parser = xml.sax.make_parser()

    if content_handler is not None:
        parser.setContentHandler(content_handler)
    if dtd_handler is not None:
        parser.setDTDHandler(dtd_handler)
    if entity_resolver is not None:
        parser.setEntityResolver(entity_resolver)
    if error_handler is not None:
        parser.setErrorHandler(error_handler)
    if locale is not None:
        parser.setLocale(locale)
    if features is not None:
        for feature, value in features.items():
            parser.setFeature(feature, value)
    if properties is not None:
        for property, value in properties.items():
            parser.setProperty(property, value)

    return parser

def parse(source, *, content_handler=None, dtd_handler=None, entity_resolver=None, error_handler=None, locale=None, features=None, properties=None):
    parser = _make_parser(content_handler=content_handler, dtd_handler=dtd_handler, entity_resolver=entity_resolver, error_handler=error_handler, locale=locale, features=features, properties=properties)

    parser.parse(source)

def parse_string(string, *, content_handler=None, dtd_handler=None, entity_resolver=None, error_handler=None, locale=None, features=None, properties=None):
    parser = _make_parser(content_handler=content_handler, dtd_handler=dtd_handler, entity_resolver=entity_resolver, error_handler=error_handler, locale=locale, features=features, properties=properties)

    inputsource = xml.sax.xmlreader.InputSource()
    if isinstance(string, str):
        inputsource.setCharacterStream(io.StringIO(string))
    else:
        inputsource.setByteStream(io.BytesIO(string))

    parser.parse(inputsource)
