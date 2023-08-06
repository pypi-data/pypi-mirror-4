import logging

from Products.CMFCore.utils import getToolByName
from plone.app.controlpanel.security import ISecuritySchema

logger = logging.getLogger('Sitesetup tools:usersandgroups')

def createGroups(portal, groups):
    """ Create user groups by passing list of tuples containing group ids and titles:

        @example groups list:

        GROUPS = [
          ('customers', 'Customers'),
          ('staff', 'Staff')
        ]

        from tools.sitesetup import createGroups
        createGroups(portal, GROUPS)

    """

    gtool = getToolByName(portal, 'portal_groups')
    for group in groups:
        gtool.addGroup(group[0], title=group[1])
    
        logger.info('"%s" group created.' % group[1])


def enableSelfRegistration(portal):
    """ Enable anonymous users to register their user account. """

    ISecuritySchema(portal).enable_self_reg = True
    logger.info('User self registration enabled.')

def enableUserPwdChoice(portal):
    """ Enable user password choice during user registration. """

    ISecuritySchema(portal).enable_user_pwd_choice = True
    logger.info('User user password choice.')
