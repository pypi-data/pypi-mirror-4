from Products.CMFPlone.utils import getToolByName

catalog = getToolByName(context, "portal_catalog")

brains = catalog(state='internally_published',
                 start=DateTime() - 1,
                 start_usage='range:min',
                 sort_on='start')
objects = map(lambda x: x.getObject(), brains)
return objects
