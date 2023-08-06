=====================
Principal Annotations
=====================

This package implements annotations for zope.security principals.
To make it clear, the `principal` here is the object that provides
``zope.security.interfaces.IPrincipal`` interface and `annotations` is
the object providing ``zope.annotation.interfaces.IAnnotations``.

The problem is that principals is dynamic, non-persistent objects created
on the fly for every security participation (request or something), so
common annotation techniques, like AttributeAnnotations cannot be applied
to them.

This package provides a persistent storage of principal annotations,
storing annotations by principal ID as well as an adapter from IPrincipal
to IAnnotations.


PrincipalAnnotationUtility
--------------------------

The core of this package is the ``PrincipalAnnotationUtility`` class
that stores annotations for principals and allows to get them easily.

It provides the IPrincipalAnnotationUtility interface::

  >>> from zope.principalannotation.interfaces import IPrincipalAnnotationUtility
  >>> from zope.principalannotation.utility import PrincipalAnnotationUtility
  >>> from zope.interface.verify import verifyObject
  >>> util = PrincipalAnnotationUtility()
  >>> verifyObject(IPrincipalAnnotationUtility, util)
  True

It provides three methods: ``getAnnotations``, ``getAnnotationsById``
and ``hasAnnotations``. Let's create a testing principal and check out
these methods::

  >>> from zope.security.testing import Principal
  >>> nadako = Principal('nadako')
  >>> nadako.id
  'nadako'

We can check if our principal has any annotations. Of course, it
currently doesn't have any::

  >>> util.hasAnnotations(nadako)
  False

We can get ``IAnnotations`` object using principal object itself::

  >>> util.getAnnotations(nadako)
  <zope.principalannotation.utility.Annotations object at 0x...>

Or using principal id::

  >>> util.getAnnotationsById(nadako.id)
  <zope.principalannotation.utility.Annotations object at 0x...>

Let's get the ``IAnnotations`` object for our principal and play with it::

  >>> annots = util.getAnnotations(nadako)

  >>> from zope.interface.verify import verifyObject
  >>> from zope.annotation.interfaces import IAnnotations
  >>> verifyObject(IAnnotations, annots)
  True

Let's check the ``IAnnotation`` contract::

  >>> bool(annots)
  False

  >>> annots['not.here']
  Traceback (most recent call last):
  ...
  KeyError: 'not.here'

  >>> annots.get('not.here') is None
  True

  >>> annots.get('not.here', 42)
  42

Note, that the ``IAnnotations`` object gets stored in the utility only
when we set a key for it. This is a simple optimization that allows
us not to store any data when all we do is simply checking for presense
of annotation. The ``hasAnnotations`` method will return ``True`` after
storing a key in the annotations::

  >>> util.hasAnnotations(nadako)
  False

  >>> annots['its.here'] = 'some info'

  >>> util.hasAnnotations(nadako)
  True

We can also delete the existing key::

  >>> del annots['its.here']

But we can't delete the key that is (no more) existant::

  >>> del annots['its.here']
  Traceback (most recent call last):
  ...
  KeyError: 'its.here'


Multiple annotation utilities
-----------------------------

Imagine that your application has a root ``site`` object with its
component registry (a.k.a. site manager) and that object has a sub-site
object with its own component registry, and that component registry
has the root's component registry as its base.

In that case, we want the ``IAnnotations`` object to be available to
retrieve annotations from higher-level utilities.

Let's register our utility in the root site and create a sub-site
with its own IPrincipalAnnotationUtility::

  >>> root['util'] = util
  >>> rootsm = root.getSiteManager()
  >>> rootsm.registerUtility(util, IPrincipalAnnotationUtility)

  >>> from zope.site.folder import Folder
  >>> from zope.site.site import LocalSiteManager

  >>> subsite = Folder()
  >>> root['subsite'] = subsite
  >>> subsm = LocalSiteManager(subsite)
  >>> subsm.__bases__ = (rootsm,)
  >>> subsite.setSiteManager(subsm)

  >>> util2 = PrincipalAnnotationUtility()
  >>> subsite['util2'] = util2
  >>> subsm.registerUtility(util2, IPrincipalAnnotationUtility)

Now, let's create a key in the IAnnotations, provided by root utility::

  >>> annots = util.getAnnotations(nadako)
  >>> annots['root.number'] = 42

The subsite utility should get the annotation successfully::

  >>> annots2 = util2.getAnnotations(nadako)
  >>> bool(annots2)
  True

  >>> annots2['root.number']
  42

If we have the key both in higher-level annotations and lower-level ones,
the lower-level will have priority, but higher-level won't be deleted or
overriden::

  >>> annots['another.number'] = 1
  >>> annots2['another.number'] = 42

  >>> annots['another.number']
  1
  >>> annots2['another.number']
  42

If we'll delete the key from lower-level, it will not be deleted from a
higher level utility::

  >>> del annots2['another.number']

  >>> annots['another.number']
  1
  >>> annots2['another.number']
  1


IPrincipal -> IAnnotations adapter
----------------------------------

Of course, the most nice feature is that we can simply adapt our
principal object to IAnnotations and get those annotations using
standard way documented in ``zope.annotation`` package.

  >>> annots = IAnnotations(nadako)
  >>> annots
  <zope.principalannotation.utility.Annotations object at 0x...>
  >>> annots['root.number']
  42

By default, the IAnnotation adapter uses the current site's utility::

  >>> IAnnotations(nadako) is util.getAnnotations(nadako)
  True

  >>> from zope.site.hooks import setSite
  >>> setSite(subsite)
  
  >>> IAnnotations(nadako) is util2.getAnnotations(nadako)
  True

Howerver, we can use a binary multi-adapter to IAnnotations to specify
some context object from which to get the annotations utility::

  >>> from zope.component import getMultiAdapter
  
  >>> annots = getMultiAdapter((nadako, root), IAnnotations)
  >>> annots is util.getAnnotations(nadako)
  True

  >>> annots = getMultiAdapter((nadako, subsite), IAnnotations)
  >>> annots is util2.getAnnotations(nadako)
  True
