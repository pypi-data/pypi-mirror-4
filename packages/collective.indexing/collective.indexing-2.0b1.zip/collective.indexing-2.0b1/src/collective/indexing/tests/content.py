from Products.ATContentTypes.content.base import ATCTContent, registerATCT
from Products.ATContentTypes.content.schemata import ATContentTypeSchema


class Foo(ATCTContent):
    """ sample content type for testing purposes """

    schema = ATContentTypeSchema.copy()
    portal_type = 'Foo'
    index_counter = 0

    def indexObject(self):
        """ overridden index method calling its super variant """
        super(Foo, self).indexObject()
        self.index_counter += 1
        assert self.index_counter < 42, 'indexing loop detected'

registerATCT(Foo, 'collective.indexing.tests')


def addFoo(container, id, **kwargs):
    """ at-constructor copied from ClassGen.py """
    obj = Foo(id)
    container._setObject(id, obj, suppress_events=True)
    obj = container._getOb(id)
    obj.manage_afterAdd(obj, container)
    obj.initializeArchetype(**kwargs)
    return obj.getId()
