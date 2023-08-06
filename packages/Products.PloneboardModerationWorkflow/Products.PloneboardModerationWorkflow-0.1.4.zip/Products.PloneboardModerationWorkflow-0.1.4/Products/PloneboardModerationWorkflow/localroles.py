# -*- coding: utf-8 -*-

from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole
from Products.PloneboardModerationWorkflow import config

from Products.CMFPlone import PloneMessageFactory as _

class ModeratorRole(object):
    implements(ISharingPageRole)
    
    title = _(u"title_moderator", default=u"Can manage forums")
    required_permission = config.DelegateModeratorRole
    
