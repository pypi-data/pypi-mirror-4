##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Implementation of Utility-baed Vocabulary Registry
"""
import zope.component
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyRegistry
from zope.schema import vocabulary
from zope.schema.interfaces import IVocabularyFactory

@implementer(IVocabularyRegistry)
class ZopeVocabularyRegistry(object):
    """IVocabularyRegistry that supports global and local utilities."""
    __slots__ = ()

    def get(self, context, name):
        """See zope.schema.interfaces.IVocabularyRegistry"""
        factory = zope.component.getUtility(IVocabularyFactory, name)
        return factory(context)

def _clear():
    """Re-initialize the vocabulary registry."""
    # This should normally only be needed by the testing framework,
    # but is also used for module initialization.
    global vocabularyRegistry
    vocabulary._clear()
    vocabularyRegistry = vocabulary.getVocabularyRegistry()
    vocabulary._clear()
    vocabulary.setVocabularyRegistry(ZopeVocabularyRegistry())

_clear()

try:
    from zope.testing import cleanup
except ImportError:
    pass
else:
    cleanup.addCleanUp(_clear)
