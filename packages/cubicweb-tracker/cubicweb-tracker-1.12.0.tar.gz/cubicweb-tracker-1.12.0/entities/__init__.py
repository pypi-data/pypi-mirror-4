"""tracker specific entities class for imported entities

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

class ProjectItemMixIn(object):
    """default mixin class for commentable objects to make them implement
    the project item interface. Defined as a mixin for use by custom tracker
    templates.
    """
    @property
    def project(self):
        return None
