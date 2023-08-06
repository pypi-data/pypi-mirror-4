try:
    from xml.etree import cElementTree as ElementTree
    if ElementTree.VERSION < '1.3.0':
        # cElementTree has no support for register_namespace
        # neither _namespace_map, thus we sacrify performance
        # for correctness
        from xml.etree import ElementTree
except ImportError:
    try:
        import cElementTree as ElementTree
    except ImportError:
        from elementtree import ElementTree

NAMESPACE = "http://schemas.xmlsoap.org/soap/envelope/"
DUMMY_NAMESPACE = "http://example.org/"

def make_soap_enveloped_saml_thingy(thingy, header_parts=None):
    """ Returns a soap envelope containing a SAML request
    as a text string.

    :param thingy: The SAML thingy
    :return: The SOAP envelope as a string
    """
    envelope = ElementTree.Element('')
    envelope.tag = '{%s}Envelope' % NAMESPACE

    if header_parts:
        header = ElementTree.Element('')
        header.tag = '{%s}Header' % NAMESPACE
        envelope.append(header)
        for part in header_parts:
            part.become_child_element_of(header)

    body = ElementTree.Element('')
    body.tag = '{%s}Body' % NAMESPACE
    envelope.append(body)

    if isinstance(thingy, basestring):
        _child = ElementTree.Element('')
        _child.tag = '{%s}FuddleMuddle' % DUMMY_NAMESPACE
        body.append(_child)
        _str = ElementTree.tostring(envelope, encoding="UTF-8")
        # find an remove the namespace definition
        i = _str.find(DUMMY_NAMESPACE)
        j = _str.rfind("xmlns:", 0, i)
        cut1 = _str[j:i+len(DUMMY_NAMESPACE)+1]
        cut2 = "<%s:FuddleMuddle />" % (cut1[6:9],)
        _str = _str.replace(cut1, "")
        return _str.replace(cut2,thingy)
    else:
        thingy.become_child_element_of(body)
        return ElementTree.tostring(envelope, encoding="UTF-8")


print make_soap_enveloped_saml_thingy("<nsx:foo xmlns:nsx=\"http://foo.org/\">bar</nsx:foo>")