from Products.CMFPlone.utils import getToolByName

catalog = getToolByName(context, "portal_catalog")

brains = catalog(review_state='internally_published',
                 start={'query':DateTime() -1,'range':'min'},
                 sort_on='start')

objects = map(lambda x: x.getObject(), brains)
return objects
