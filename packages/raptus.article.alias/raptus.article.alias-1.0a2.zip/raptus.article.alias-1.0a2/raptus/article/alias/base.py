from Products.CMFCore.utils import getToolByName

class ProviderMixin(object):

    def convertAliasBrains(self, brains):
        converted = []
        catalog = getToolByName(self.context, 'portal_catalog')
        for brain in brains:
            if brain.meta_type == 'Alias':
                ref = brain.getObject().getReference()
                if ref is None:
                    continue
                results = catalog(UID=ref.UID())
                if not len(results):
                    continue
                refbrain = results[0]
                if not 'alias' in refbrain:
                    refbrain.__record_schema__['alias'] = max(refbrain.__record_schema__.values()) + 1
                refbrain.alias = brain
                converted.append(refbrain)
            else:
                converted.append(brain)
        return converted
