from lxml import html, etree
import cgi
import re


SELF_CLOSING_TAGS = ('area', 'base', 'basefont', 'br', 'col', 'frame', 'hr', 'input', 'image', 'link', 'meta', 'param')


def bleach(text, allowed_tags, allowed_attributes={}, allowed_styles={}, strip=False):
    def wildcard_match(patterns, string):
        return any([re.match(pattern.replace('*', '.*'), string) for pattern in patterns if '*' in pattern])

    doc = html.fragment_fromstring(text, create_parent=True)
    for element in doc.iter():
        if not isinstance(element.tag, basestring):
            element.drop_tree()
            continue
        tag = element.tag.lower()
        if tag in allowed_tags:
            for attrib in element.attrib.keys():
                attrib = attrib.lower()
                if isinstance(allowed_attributes, dict):
                    attribs = allowed_attributes.get('*', []) + allowed_attributes.get(tag, [])
                else:
                    attribs = allowed_attributes
                if attrib not in attribs and not wildcard_match(attribs, attrib):
                    del element.attrib[attrib]
                elif attrib == 'style':
                    style = element.attrib['style']
                    lines = [line for line in style.split(';') if ':' in line]
                    properties = {}
                    for line in lines:
                        property, value = [word.strip().lower() for word in line.split(':')]
                        if isinstance(allowed_styles, dict):
                            props = allowed_styles.get('*', []) + allowed_styles.get(tag, [])
                        else:
                            props = allowed_styles
                        if property in props or wildcard_match(props, property):
                            properties[property] = value
                    styles = [u'%s: %s;' % (property, value) for property, value in properties.items()]
                    if styles:
                        element.attrib['style'] = ' '.join(styles)
                    else:
                        del element.attrib['style']
        elif element.getparent() is not None:
            if strip:
                element.drop_tree()
            else:
                attribs = "".join(u' %s="%s"' % (attrib, value) for attrib, value in element.attrib.items())
                text = element.text.strip() if element.text else ''
                tail = element.tail.strip() if element.tail else ''
                text_dict = {'tag': tag, 'attribs': attribs, 'text': text, 'tail': tail}
                if tag in SELF_CLOSING_TAGS:
                    element.text = u'<%(tag)s%(attribs)s />' % text_dict
                else:
                    element.text = u'<%(tag)s%(attribs)s>%(text)s' % text_dict
                    element.tail = u'</%(tag)s>%(tail)s' % text_dict
                element.drop_tag()
    return _tostring(doc)


def replace_elements(text, element_replacements={}):
    if element_replacements:
        doc = html.fragment_fromstring(text, create_parent=True)
        selection = ','.join(element_replacements.keys())
        for element in doc.cssselect(selection):
            element.tag = element_replacements[element.tag]
        return _tostring(doc)
    else:
        return text


def remove_empty_paragraphs(text):
    doc = html.fragment_fromstring(text, create_parent=True)
    for element in doc.cssselect('p'):
        text = element.text_content()
        text = text.strip()
        if text == '' and len(element) == 0:
            element.drop_tree()
    return _tostring(doc)


def _tostring(doc):
    clean = doc.text or u''
    for child in doc.getchildren():
        clean += etree.tounicode(child)
    clean = clean.replace('\r', '')
    clean = clean.replace('\t', '')
    clean = clean.replace('&#13;', '')
    clean = clean.replace('&nbsp;', '')
    clean = clean.replace('&#160;', '')
    return clean
