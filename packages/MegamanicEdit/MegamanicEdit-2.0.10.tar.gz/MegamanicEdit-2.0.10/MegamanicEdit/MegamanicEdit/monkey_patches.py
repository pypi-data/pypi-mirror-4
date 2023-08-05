from Products.Archetypes.Schema import Schemata

old_filterFields = Schemata.filterFields.im_func

def filterFields(self, *predicates, **values):
    result = old_filterFields(self, *predicates, **values)
    result2 = []
    import pdb; pdb.set_trace()
    this = self.this()
    if hasattr(this.aq_base, 'isMegamanicEditable') and \
            this.isMegamanicEditable():
        for field in result:
            try:
                if field.get(self):
                    result2.append(field)
            except:
                # Something went wrong, but the
                # field was available so lets
                # juts pass it along
                result2.append(field)
        return result2
    return result

Schemata.filterFields = filterFields
