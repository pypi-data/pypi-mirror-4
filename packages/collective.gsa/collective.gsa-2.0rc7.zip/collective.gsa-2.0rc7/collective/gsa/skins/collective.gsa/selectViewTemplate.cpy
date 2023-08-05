## Script (Python) "selectViewTemplate"
##title=Helper method to select a view template
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=templateId

from Products.CMFPlone import PloneMessageFactory as _
context.setLayout(templateId)

gsa_reindex = context.restrictedTraverse("@@gsa-reindex")
if gsa_reindex:
    gsa_reindex()

context.plone_utils.addPortalMessage(_(u'View changed.'))
return state
