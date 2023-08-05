from Products.AccessibleReferenceBrowserWidget.implements_arbw import implements_arbw

if not implements_arbw()(context): raise TypeError, 'interface not implemented'

return context.get_reference_field().getAccessor(context)() and True
