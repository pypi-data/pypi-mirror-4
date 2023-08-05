from zope.interface import Interface

class IAccessibleReferenceBrowserWidget(Interface):
    """Marker interface."""

    def get_reference_field():
        """Gets the reference field to provide a widget for."""


