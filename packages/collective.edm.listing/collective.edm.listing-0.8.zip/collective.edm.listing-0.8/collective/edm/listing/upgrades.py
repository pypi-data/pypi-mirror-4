from Products.CMFCore.utils import getToolByName

def cook_resources(context):
    getToolByName(context, 'portal_css').cookResources()
    getToolByName(context, 'portal_javascripts').cookResources()

