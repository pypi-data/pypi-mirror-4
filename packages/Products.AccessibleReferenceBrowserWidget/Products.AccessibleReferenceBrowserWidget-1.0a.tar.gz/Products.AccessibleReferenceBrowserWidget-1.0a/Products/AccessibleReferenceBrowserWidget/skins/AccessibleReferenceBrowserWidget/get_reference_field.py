from Products.AccessibleReferenceBrowserWidget.implements_arbw import implements_arbw

if not implements_arbw()(context): return None

for field in context.Schema().fields():
    if field.getType() == 'Products.Archetypes.Field.ReferenceField':
      return field
