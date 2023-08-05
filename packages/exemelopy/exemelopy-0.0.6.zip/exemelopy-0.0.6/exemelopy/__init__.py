import cgi
import re
from uuid import UUID

from lxml import etree

try:
    from io import BytesIO  # python 3
except ImportError:
    try:
        from cStringIO import StringIO as BytesIO
    except ImportError:
        from StringIO import StringIO as BytesIO


__all__ = (
    'XMLEncoder',
    )



class XMLEncoder(object):
    """The main constructor method which accepts the value
    of ``data`` to be later converted to XML.

    The document element ``doc_el`` can be changed from the
    default 'document' to any valid XML element name.

    The ``encoding`` defaults to 'UTF-8', but can be changed
    to any value accepted by ``lxml.etree``.

    Setting ``strict_errors`` to ``True`` will cause a ``TypeError``
    to be raised for unsupported types.

    Any other keyword arguments are passed directly to the
    set-up method of ``lxml.etree``.
    """

    _is_uuid = re.compile(r'^\{?([0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12})\}?$', re.I)

    def __init__(self, data, doc_el='document', encoding='UTF-8', strict_errors=False, **params):
        self.data = data
        self.document = etree.Element(doc_el, **params)
        self.encoding = encoding
        self.strict_errors = strict_errors


    def to_string(self, indent=True, declaration=True):
        """Encodes the stored ``data`` to XML and returns a
        ``string``.

        Setting ``indent`` to ``False`` will forego any pretty-printing
        and return a condensed value.

        Setting ``declaration`` to ``False`` will skip inserting the
        XML declaration.
        """
        return etree.tostring(self.to_xml(),
                              encoding=self.encoding,
                              xml_declaration=declaration,
                              pretty_print=indent
                              )


    def to_xml(self):
        """Encodes the stored ``data`` to XML and returns
        an ``lxml.etree`` value.
        """
        if self.data:
            self.document = self._update_document(self.document, self.data)
        return self.document


    def from_string(self, string):
        """Parses a ``string`` value which replaces the internal ``data`` value."""
        self.document = etree.parse(BytesIO(string))


    def _update_document(self, node, data):

        if data is None:
            node.text = None

        elif data is True:
            node.set('nodetype', u'boolean')
            node.text = u"true"

        elif data is False:
            node.set('nodetype', u'boolean')
            node.text = u"false"

        elif isinstance(data, basestring) and \
             len(data) in (36, 38) and \
             self._is_uuid.match(data):

            try:
                UUID(data)
            except:
                pass
            else:
                node.set('nodetype', u'uuid')
            finally:
                node.text = self._to_unicode(data)

        elif hasattr(data, 'isoformat'):
            try:
                node.text = data.isoformat()
                node.set('nodetype', u'timestamp')
            except TypeError:
                pass

        elif self._is_scalar(data):
            node.text = self._to_unicode(data)

        elif isinstance(data, BytesIO):
            node.text = self._to_unicode(data.getvalue())

        elif hasattr(data, 'iteritems'):
            for name, items in data.iteritems():
                try:
                    if isinstance(name, basestring) and name and str(name[0]) is '?':
                        #  processing instruction
                        self._add_processing_instruction(node, items)

                    elif isinstance(name, basestring) and name and str(name[0]) is '!':
                        # doctype
                        self._add_doctype(node, items)

                    elif isinstance(name, basestring) and name and not name[0].isalpha():
                        child = etree.SubElement(node, u'node', name=unicode(name))

                    elif isinstance(name, basestring) and name:
                        child = etree.SubElement(node, unicode(name))

                except ValueError:
                    # node name is invalid, use <node name="{name}">
                    child = etree.SubElement(node, u"node", name=unicode(name))

                child = self._update_document(child, items)

        elif isinstance(data, list):
            node.set('nodetype',u'list')
            for item in data:
                self._update_document(
                    etree.SubElement(node, u'i'),
                    item)

        elif isinstance(data, set):
            node.set('nodetype',u'unique-list')
            for item in data:
                self._update_document(
                    etree.SubElement(node, u'i'),
                    item)


        elif isinstance(data, tuple):
            node.set('nodetype',u'fixed-list')
            for item in data:
                self._update_document(
                    etree.SubElement(node, u'i'),
                    item)


        elif hasattr(data, 'send'):
            # generator
            node.set('nodetype',u'generated-list')
            for item in data:
                self._update_document(
                    etree.SubElement(node, u'i'),
                    item)


        elif isinstance(data, object) \
            and hasattr(data, '__slots__'):
            children = ((n, getattr(data, n))
                        for n in data.__slots__
                        if n[0] is not '_' and not hasattr(n, '__call__'))

            sub = etree.SubElement(node,
                                   unicode(data.__class__.__name__),
                                   nodetype="container")

            for item, value in children:
                self._update_document(
                    etree.SubElement(sub, unicode(item)),
                    value)


        elif isinstance(data, object):
            try:
                children = ((n, v)
                            for n, v in data.__dict__.iteritems()
                            if n[0] is not '_' and not hasattr(n, '__call__'))


                sub = etree.SubElement(node,
                                       unicode(data.__class__.__name__),
                                       nodetype="container")

                for item, value in children:
                    self._update_document(
                        etree.SubElement(sub, unicode(item)),
                        value)

            except AttributeError as e:
                if self.strict_errors:
                    raise TypeError('%s is not XML serializable' % type(data))

                node.set('nodetype', u'unsupported-type')
                node.text = self._to_unicode(type(data))


        else:
            if self.strict_errors:
                raise TypeError('%s is not XML serializable' % type(data))

            node.set('nodetype', u'unsupported-type')
            node.text = self._to_unicode(type(data))

        return node


    def _is_scalar(self, value):
        return isinstance(value, (basestring, float, int, long))


    def _to_unicode(self, string):
        if not string and not self._is_scalar(string):
            return u''

        return unicode(self.__escape(string))


    def _add_processing_instruction(self, node, data):
        raise NotImplemented('creating processing instructions has not been implemented')

        self.document = etree.ElementTree(self.document)

        attrs = []

        if type(data) is dict:
            attrs = self.__dict_to_attrs(dict(
                (name, value)
                for name, value in data.iteritems()
                if name[0].isalpha() and type(value) is not dict
                ))

        pi = etree.ProcessingInstruction(node[1:])#, ' '.join(attrs))


    def __dict_to_attrs(self, d):
        return ('%s="%s"' % (name, value) for name, value in d.iteritems())


    def _add_doctype(self, *args, **kwargs):
        raise NotImplemented('creating doctype declarations has not been implemented')


    def __escape(self, data):
        if data is None:
            return None

        if isinstance(data, unicode):
            return data

        if isinstance(data, str):
            try:
                data = unicode(data, 'latin1')
            except:
                pass

        return data


    def __unicodeToHTMLEntities(self, text):
        """Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
        return cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
