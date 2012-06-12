import copy

from dictshield.document import Document


class View(object):

    def __init__(self, document):
        self.document = document


class WhitelistView(View):

    def __getattr__(self, field):
        if field in self.fields:
            return getattr(self.document, field)
        else:
            raise AttributeError("%r object has no attribute %r"
                % (self.__class__.__name__, field))

    def to_json(self, *args, **kwargs):
        filtered_document = self._get_filtered_document()

        return filtered_document.to_json(*args, **kwargs)

    def _get_filtered_document(self):
        FilteredDocumentClass = self._get_filtered_document_class()

        filtered_document = FilteredDocumentClass()

        for k, v in self.document.to_python().items():
            setattr(filtered_document, k, v)

        return filtered_document

    def _get_filtered_document_class(self):
        class FilteredDocumentClass(Document): pass

        FilteredDocumentClass._fields = dict([
            (k, getattr(self.document.__class__, k))
            for k in self.document._fields
            if k in self.fields
        ])

        return FilteredDocumentClass

