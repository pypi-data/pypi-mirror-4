"""tracker specific hooks

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb import ValidationError
from cubicweb.utils import transitive_closure_of
from cubicweb.schema import META_RTYPES
from cubicweb.selectors import is_instance
from cubicweb.server import hook
from cubicweb.hooks import notification

from cubes.localperms import hooks as localperms

# automatization hooks #########################################################

class VersionStatusChangeHook(hook.Hook):
    """when a ticket is done, automatically set its version'state to 'dev' if
      necessary
    """
    __regid__ = 'version_status_change_hook'
    __select__ = hook.Hook.__select__ & hook.match_rtype('in_state',)
    events = ('after_add_relation',)
    ticket_states_start_version = set(('in-progress',))

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidfrom)
        if entity.e_schema != 'Ticket':
            return
        iwf = entity.cw_adapt_to('IWorkflowable')
        if iwf.state in self.ticket_states_start_version \
               and entity.in_version():
            versioniwf = entity.in_version().cw_adapt_to('IWorkflowable')
            if any(tr for tr in versioniwf.possible_transitions()
                   if tr.name == 'start development'):
                versioniwf.fire_transition('start development')


class TicketDoneInChangeHook(hook.Hook):
    """when a ticket is attached to a version and it's identical to another one,
    attach the other one as well
    """
    __regid__ = 'ticket_done_in_change'
    __select__ = hook.Hook.__select__ & hook.match_rtype('done_in',)
    events = ('after_add_relation',)

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidfrom)
        execute = entity._cw.execute
        for identic in entity.identical_to:
            iversion = identic.in_version()
            iveid = iversion and iversion.eid
            if iveid != self.eidto:
                try:
                    execute('SET X done_in V WHERE X eid %(x)s, V eid %(v)s',
                            {'x': identic.eid, 'v': self.eidto})
                except:
                    self.exception("can't synchronize version")


class TicketStatusChangeHook(hook.Hook):
    """when a ticket status change and it's identical to another one, change the
    state of the other one as well
    """
    __regid__ = 'ticket_status_change_hook'
    __select__ = hook.Hook.__select__ & is_instance('TrInfo')
    events = ('after_add_entity',)

    def __call__(self):
        trinfo = self.entity
        forentity = trinfo.for_entity
        if forentity.e_schema != 'Ticket' or not forentity.identical_to:
            return
        synchronized = self._cw.transaction_data.setdefault(
            'ticket_wf_synchronized', set())
        if forentity.eid in synchronized:
            return
        synchronized.add(forentity.eid)
        pstate = trinfo.previous_state
        tr = trinfo.transition
        for identic in forentity.identical_to:
            if identic.eid in synchronized:
                continue
            idiwf = identic.cw_adapt_to('IWorkflowable')
            if idiwf.current_state and idiwf.current_state.eid == pstate.eid:
                idiwf.fire_transition_if_possible(tr.name, trinfo.comment,
                                                  trinfo.comment_format)


# verification hooks ###########################################################

class CheckProjectCyclesHook(hook.Hook):
    __regid__ = 'check_project_cycles'
    __select__ = hook.Hook.__select__ & hook.match_rtype('subproject_of',)
    events = ('before_add_relation',)

    def __call__(self):
        # detect cycles
        proj = self._cw.entity_from_eid(self.eidfrom)
        for child in transitive_closure_of(proj, 'reverse_subproject_of'):
            if self.eidto == child.eid:
                msg = self._cw._('you cannot link these entities, they would form a cycle')
                raise ValidationError(self.eidto, {'child' : msg})


# notification hooks ###########################################################

class BeforeUpdateVersion(notification.EntityUpdateHook):
    __regid__ = 'before_update_version'
    __select__ = notification.EntityUpdateHook.__select__ & is_instance('Version')
    skip_attrs = META_RTYPES | set(('description', 'description_format', 'num'))

class BeforeUpdateTicket(notification.EntityUpdateHook):
    __regid__ = 'before_update_ticket'
    __select__ = notification.EntityUpdateHook.__select__ & is_instance('Ticket')
    skip_attrs = META_RTYPES | set(('done_in', 'concerns', 'description_format'))

class BeforeInVersionChangeHook(hook.Hook):
    __regid__ = 'before_in_version_change'
    __select__ = hook.Hook.__select__ & hook.match_rtype('done_in',)
    events = ('before_add_relation',)

    def __call__(self):
        if self.eidfrom in self._cw.transaction_data.get('neweids', ()):
            return # entity is being created
        changes = self._cw.transaction_data.setdefault('changes', {})
        thisentitychanges = changes.setdefault(self.eidfrom, set())
        oldrset = self._cw.execute("Any VN WHERE V num VN, T done_in V, T eid %(eid)s",
                                  {'eid': self.eidfrom})
        oldversion = oldrset and oldrset[0][0] or None
        newrset = self._cw.execute("Any VN WHERE V num VN, V eid %(eid)s",
                                  {'eid': self.eidto})
        newversion = newrset[0][0]
        if oldversion != newversion:
            thisentitychanges.add(('done_in', oldversion, newversion))
            notification.EntityUpdatedNotificationOp(self._cw)


# require_permission propagation hooks #########################################

# bw compat
S_RELS = localperms.S_RELS
O_RELS = localperms.O_RELS
SKIP_S_RELS = localperms.SKIP_S_RELS
SKIP_O_RELS = localperms.SKIP_O_RELS

# not necessary on:
#
# * "secondary" relations: todo_by, done_in, appeared_in, depends_on, uses
# * no propagation needed: wf_info_for
#
# XXX: see_also
O_RELS |= set(('concerns', 'version_of', 'subproject_of'))
