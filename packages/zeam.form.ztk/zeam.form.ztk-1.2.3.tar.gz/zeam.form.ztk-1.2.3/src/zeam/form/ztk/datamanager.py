# -*- coding: utf-8 -*-

from zope.interface import alsoProvides
from zeam.form.base.datamanager import BaseDataManager


def makeGenericAdaptiveDataManager(*fields):

    class GenericAdaptiveDataManager(BaseDataManager):
        """A data manager that adapt its content to an interface
        before doing anything.
        """
        def __init__(self, content):
            self.fields = {}
            self.adapters = {}
            for field in fields:
                interface = field._field.interface
                self.fields[field.identifier] = interface
                if (not interface.providedBy(content) and
                    not interface in self.adapters):
                    alsoProvides(self, interface)
                    self.adapters[interface] = interface(content)
            self.content = content

        def _getAdapter(self, identifier):
            if not identifier in self.fields:
                return self.content
            return self.adapters.get(self.fields.get(identifier))

        def get(self, identifier):
            content = self._getAdapter(identifier)
            if content is not None:
                try:
                    return getattr(content, identifier)
                except AttributeError:
                    pass
            raise KeyError(identifier)

        def set(self, identifier, value):
            content = self._getAdapter(identifier)
            if content is None:
                raise KeyError(identifier)
            setattr(content, identifier, value)

        def delete(self, identifier):
            content = self._getAdapter(identifier)
            if content is not None:
                try:
                    return delattr(content, identifier)
                except AttributeError:
                    pass
            raise KeyError(identifier)


    return GenericAdaptiveDataManager
