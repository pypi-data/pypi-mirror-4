"""tracker specific entities class for Ticket

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from rql import nodes
from cubicweb.entities import AnyEntity


class Ticket(AnyEntity):
    __regid__ = 'Ticket'
    __permissions__ = ('developer', 'client')
    fetch_attrs = ('title', 'type', 'priority', 'in_state')

    OPEN_STATES = frozenset(('created', 'in-progress',))

    @classmethod
    def cw_fetch_order(cls, select, attr, var):
        if attr == 'priority':
            func = nodes.Function('priority_sort_value')
            func.append(nodes.variable_ref(var))
            sterm = nodes.SortTerm(func, asc=False)
            select.add_sort_term(sterm)
        elif attr in ('title', 'type'):
            select.add_sort_var(var)

    @property
    def project(self):
        """project item interface"""
        return self.concerns[0]

    # dublin core #############################################################

    def dc_title(self):
        return u'#%s %s' % (self.eid, self.title)

    def dc_long_title(self):
        return u'%s %s' % (self.project.name, self.dc_title())

    # ticket'specific logic ###################################################


    def is_open(self):
        return self.cw_adapt_to('IWorkflowable').state in self.OPEN_STATES

    def state_history(self):
        """returns a list of dates where the state changed from "open" to "not-open"
        :returns: a list couples of (date, is_open)
        """
        dates = [(self.creation_date, True)]
        for tr_info in self.reverse_wf_info_for:
            prevstate = tr_info.previous_state.name
            nextstate = tr_info.new_state.name
            if prevstate in self.OPEN_STATES and nextstate not in self.OPEN_STATES:
                dates.append( (tr_info.creation_date, False) )
            elif prevstate not in self.OPEN_STATES and nextstate in self.OPEN_STATES:
                dates.append( (tr_info.creation_date, True) )
        return sorted(dates)

    def in_version(self):
        versions = self.done_in
        if versions:
            return versions[0]

    def next_version(self):
        version = self.in_version()
        if version:
            return version.next_version()
        return self.project.versions_in_state(('planned', 'dev'), True)

    def sortvalue(self, rtype=None):
        if rtype == 'priority':
            return ['minor', 'normal', 'important'].index(self.priority)
        if rtype is None:
            return self.eid
        return super(Ticket, self).sortvalue(rtype)
