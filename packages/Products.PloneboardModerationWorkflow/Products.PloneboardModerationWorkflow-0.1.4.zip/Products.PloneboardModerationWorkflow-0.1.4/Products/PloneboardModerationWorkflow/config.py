# -*- coding: utf-8 -*-

from Products.CMFCore.permissions import setDefaultRoles
from AccessControl import ModuleSecurityInfo

security = ModuleSecurityInfo("Products.PloneboardModerationWorkflow.config")

#security.declarePublic("DelegateModeratorRole")
#DelegateModeratorRole = "Sharing page: Delegate Moderator role"
#setDefaultRoles(DelegateModeratorRole, ('Manager',))
