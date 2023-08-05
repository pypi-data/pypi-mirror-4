"""Common configuration constants
"""
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'raptus.article.alias'

security = ModuleSecurityInfo('raptus.article.alias.config')

security.declarePublic('ADD_PERMISSION')
ADD_PERMISSION = 'raptus.article: Add Alias'
setDefaultRoles(ADD_PERMISSION, ('Manager','Contributor',))
