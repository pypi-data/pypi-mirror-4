from lxml import etree
from meta import DocumentMeta, BaseDocumentSession

root = etree.Element('root')

class XMLDocument(object):
    """
        XML Document base class
    """

    __metaclass__ = DocumentMeta

    def __init__(self, **kwargs):

        row = etree.Element(self.__class__.__name__)
        root.append(row)

        for key, value in kwargs.iteritems():

            element = etree.Element(key)
            element.text = value
            row.append(element)


class Session(BaseDocumentSession):
    """
        A class featuring a database session
    """

    def commit(self):
        """
            Dumps the scraped data to the filesystem
        """

        with open(self.file_name, "w") as f:
            f.writelines(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8'))

    def close(self):
        pass


xml_session = Session()
