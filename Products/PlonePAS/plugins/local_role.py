##############################################################################
#
# PlonePAS - Adapt PluggableAuthService for use in Plone
# Copyright (C) 2005 Enfold Systems, Kapil Thangavelu, et al
# Portions Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

A Local Roles Plugin Implementation that respects Black Listing markers.

ie. containers/objects which denote that they do not wish to acquire local
roles from their containment structure.

$Id$
"""

from sets import Set
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent
from Globals import DTMLFile, InitializeClass

from zope.interface import implementedBy

from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.LocalRolePlugin import LocalRolePlugin
from Products.PlonePAS.interfaces.plugins import ILocalRolesPlugin

def manage_addLocalRolesManager( dispatcher, id, title=None, RESPONSE=None):
    """
    add a local roles manager
    """

    lrm = LocalRolesManager( id, title )
    dispatcher._setObject( lrm.getId(), lrm)

    if RESPONSE is not None:
        RESPONSE.redirect('manage_workspace')

manage_addLocalRolesManagerForm = DTMLFile('../zmi/LocalRolesManagerForm', globals())

class LocalRolesManager(LocalRolePlugin):
    """Class incorporating local role storage with
    PlonePAS-specific local role permission checking.
    """

    meta_type = "Local Roles Manager"
    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self._id = self.id = id
        self.title = title

    #security.declarePrivate( 'getRolesInContext' )
    def getRolesInContext( self, user, object):
        user_id = user.getId()
        group_ids = user.getGroups()

        principal_ids = list( group_ids )
        principal_ids.insert( 0, user_id )

        local ={}
        object = aq_inner( object )

        while 1:
            local_roles = getattr( object, '__ac_local_roles__', None )

            if local_roles:
                if callable( local_roles ):
                    local_roles = local_roles()

                dict = local_roles or {}

                for principal_id in principal_ids:
                    for role in dict.get( principal_id, [] ):
                        local[ role ] = 1

            inner = aq_inner( object )
            parent = aq_parent( inner )

            if getattr(object, '__ac_local_roles_block__', None):
                break

            if parent is not None:
                object = parent
                continue

            new = getattr( object, 'im_self', None )

            if new is not None:
                object = aq_inner( new )
                continue

            break

        return list( user.getRoles() ) + local.keys()

    #security.declarePrivate( 'checkLocalRolesAllowed' )
    def checkLocalRolesAllowed( self, user, object, object_roles ):
        # Still have not found a match, so check local roles. We do
        # this manually rather than call getRolesInContext so that
        # we can incur only the overhead required to find a match.
        inner_obj = aq_inner( object )
        user_id = user.getId()
        # [ x.getId() for x in user.getGroups() ]
        group_ids = user.getGroups()

        principal_ids = list( group_ids )
        principal_ids.insert( 0, user_id )

        while 1:

            local_roles = getattr( inner_obj, '__ac_local_roles__', None )

            if local_roles:
                if callable( local_roles ):
                    local_roles = local_roles()

                dict = local_roles or {}

                for principal_id in principal_ids:
                    local_roles = dict.get( principal_id, [] )

                    for role in object_roles:

                        if role in local_roles:
                            if user._check_context( object ):
                                return 1

                            return 0

            inner = aq_inner( inner_obj )
            parent = aq_parent( inner )

            if getattr(inner_obj, '__ac_local_roles_block__', None):
                break

            if parent is not None:
                inner_obj = parent
                continue

            new = getattr( inner_obj, 'im_self', None )

            if new is not None:
                inner_obj = aq_inner( new )
                continue

            break

        return None

    def getAllLocalRolesInContext(self, context):
        roles = {}
        object = aq_inner( context )

        while True:

            local_roles = getattr(object, '__ac_local_roles__', None)

            if local_roles:
                if callable( local_roles ):
                    local_roles = local_roles()

                dict = local_roles or {}

                for principal, localroles in dict.items():
                    if not principal in roles:
                        roles[principal]=Set()

                    roles[principal].update(localroles)

            inner = aq_inner( object )
            parent = aq_parent( inner )

            if getattr(object, '__ac_local_roles_block__', None):
                break

            if parent is not None:
                object = parent
                continue

            new = getattr( object, 'im_self', None )

            if new is not None:
                object = aq_inner( new )
                continue

            break

        return roles

classImplements(LocalRolesManager,
                ILocalRolesPlugin, *implementedBy(LocalRolePlugin))

InitializeClass(LocalRolesManager)
