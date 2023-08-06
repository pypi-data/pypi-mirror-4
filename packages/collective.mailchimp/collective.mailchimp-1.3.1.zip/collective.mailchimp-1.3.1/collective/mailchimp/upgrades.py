from Products.CMFCore.utils import getToolByName

from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from collective.mailchimp.interfaces import IMailchimpSettings


def update_registry(context):
    registry = getUtility(IRegistry)
    registry.registerInterface(IMailchimpSettings)


def install_mailchimp_stylesheet(context):
    csstool = getToolByName(context, 'portal_css', None)
    stylesheet_id = \
        '++resource++collective.mailchimp.stylesheets/mailchimp.css'
    if stylesheet_id not in csstool.getResourceIds():
        csstool.manage_addStylesheet(
            id=stylesheet_id,
            rel='stylesheet',
            rendering='link',
            enabled=True,
            cookable=True,
        )
