##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Implementation of IPrincipalAnnotationUtility
"""
__docformat__ = 'restructuredtext'
from BTrees.OOBTree import OOBTree
from persistent import Persistent
from persistent.dict import PersistentDict
from zope import interface, component
from zope.annotation.interfaces import IAnnotations
from zope.location import Location
from zope.location.interfaces import IContained
from zope.security.interfaces import IPrincipal
from zope.site.next import queryNextUtility

from zope.principalannotation.interfaces import IPrincipalAnnotationUtility

# TODO: register utility as adapter for IAnnotations on utility activation.

@interface.implementer(IPrincipalAnnotationUtility, IContained)
class PrincipalAnnotationUtility(Persistent):
    """Stores `IAnnotations` for `IPrinicipals`.

    The utility ID is 'PrincipalAnnotation'.
    """

    __parent__ = None
    __name__ = None

    def __init__(self):
        self.annotations = OOBTree()

    def getAnnotations(self, principal):
        """Return object implementing IAnnotations for the given principal.

        If there is no `IAnnotations` it will be created and then returned.
        """
        return self.getAnnotationsById(principal.id)

    def getAnnotationsById(self, principalId):
        """Return object implementing `IAnnotations` for the given principal.

        If there is no `IAnnotations` it will be created and then returned.
        """
        annotations = self.annotations.get(principalId)
        if annotations is None:
            annotations = Annotations(principalId, store=self.annotations)
            annotations.__parent__ = self
            annotations.__name__ = principalId
        return annotations

    def hasAnnotations(self, principal):
        """Return boolean indicating if given principal has `IAnnotations`."""
        return principal.id in self.annotations


@interface.implementer(IAnnotations)
class Annotations(Persistent, Location):
    """Stores annotations."""

    def __init__(self, principalId, store=None):
        self.principalId = principalId
        self.data = PersistentDict() # We don't really expect that many

        # _v_store is used to remember a mapping object that we should
        # be saved in if we ever change
        self._v_store = store

    def __bool__(self):
        nz = bool(self.data)
        if not nz:
            # maybe higher-level utility's annotations will be non-zero
            next = queryNextUtility(self, IPrincipalAnnotationUtility)
            if next is not None:
                annotations = next.getAnnotationsById(self.principalId)
                return bool(next)
        return nz

    __nonzero__ = __bool__

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            # We failed locally: delegate to a higher-level utility.
            next = queryNextUtility(self, IPrincipalAnnotationUtility)
            if next is not None:
                annotations = next.getAnnotationsById(self.principalId)
                return annotations[key]
            raise

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        if getattr(self, '_v_store', None) is not None:
            # _v_store is used to remember a mapping object that we should
            # be saved in if we ever change
            self._v_store[self.principalId] = self
            del self._v_store

        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]


@component.adapter(IPrincipal)
@interface.implementer(IAnnotations)
def annotations(principal, context=None):
    utility = component.getUtility(IPrincipalAnnotationUtility, context=context)
    return utility.getAnnotations(principal)
