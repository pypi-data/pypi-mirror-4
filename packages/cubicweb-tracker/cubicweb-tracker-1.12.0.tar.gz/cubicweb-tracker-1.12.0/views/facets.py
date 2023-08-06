"""facets to search content

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.selectors import is_instance
from cubicweb.web.facet import RelationFacet, AttributeFacet, DateRangeFacet

class TicketConcernsFacet(RelationFacet):
    __regid__ = 'concerns-facet'
    __select__ = RelationFacet.__select__ & is_instance('Ticket')
    rtype = 'concerns'
    target_attr = 'name'


class TicketDoneInFacet(RelationFacet):
    __regid__ = 'done_in-facet'
    __select__ = RelationFacet.__select__ & is_instance('Ticket')
    rtype = 'done_in'
    target_attr = 'num'
    sortfunc = 'VERSION_SORT_VALUE'
    sortasc = False
    no_relation_label = _('<not planned>')


class TicketPriorityFacet(AttributeFacet):
    __regid__ = 'priority-facet'
    __select__ = AttributeFacet.__select__ & is_instance('Ticket')
    rtype = 'priority'
    sortfunc = 'PRIORITY_SORT_VALUE'


class TicketTypeFacet(AttributeFacet):
    __regid__ = 'type-facet'
    __select__ = AttributeFacet.__select__ & is_instance('Ticket')
    rtype = 'type'


class TicketDateFacet(DateRangeFacet):
    __regid__ = 'date-facet'
    __select__ = DateRangeFacet.__select__ & is_instance('Ticket')
    rtype = 'creation_date'
