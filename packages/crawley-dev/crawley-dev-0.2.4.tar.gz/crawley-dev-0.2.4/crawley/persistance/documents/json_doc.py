try:
    import simplejson
except ImportError:
    import json as simplejson

from meta import DocumentMeta, BaseDocumentSession

json_objects = []

class JSONDocument(object):
    """
        JSON Document base class
    """

    __metaclass__ = DocumentMeta

    def __init__(self, **kwargs):

        json_objects.append(kwargs)


class Session(BaseDocumentSession):
    """
        A class featuring a database session
    """

    def commit(self):
        """
            Dumps the scraped data to the filesystem
        """
        with open(self.file_name, 'w') as f:
            simplejson.dump(json_objects, f)

    def close(self):
        pass


json_session = Session()
