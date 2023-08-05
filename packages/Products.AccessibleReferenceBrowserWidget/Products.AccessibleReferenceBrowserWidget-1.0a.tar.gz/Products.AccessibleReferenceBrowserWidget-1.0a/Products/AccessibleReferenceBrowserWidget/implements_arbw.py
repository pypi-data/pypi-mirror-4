from interfaces import IAccessibleReferenceBrowserWidget

class implements_arbw:

    def __call__(self, object_):
        return IAccessibleReferenceBrowserWidget.providedBy(object_)
