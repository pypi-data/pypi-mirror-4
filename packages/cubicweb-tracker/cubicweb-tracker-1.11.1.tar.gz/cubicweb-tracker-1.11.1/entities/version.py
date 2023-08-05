"""tracker version entity class

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.decorators import cached
from logilab.common.date import todate

from rql import nodes

from cubicweb import ValidationError
from cubicweb.entities import AnyEntity
from cubicweb.entities.adapters import IUserFriendlyUniqueTogether
from cubicweb.selectors import is_instance

from cubes.iprogress.entities import IProgressAdapter


class VersionIProgressAdapter(IProgressAdapter):
    __select__ = is_instance('Version')

    def progress_info(self):
        """returns a dictionary describing load and progress of the version"""
        return {'notestimated': 0,
                'estimated': 0,
                'done': 0,
                'todo': 0 }

    def finished(self):
        return self.entity.cw_adapt_to('IWorkflowable').state in self.entity.FINISHED_STATES

    def progress_class(self):
        """return a class name according to % progress of a version"""
        progress = self.progress()
        if progress == 100:
            return 'complete'
        elif progress == 0:
            return 'none'
        elif progress > 50:
            return 'over50'
        return 'below50'


class VersionIMileStoneAdapter(VersionIProgressAdapter):
    __regid__ = 'IMileStone'
    parent_type = 'Project'

    def contractors(self):
        return self.entity.todo_by

    def in_progress(self):
        return self.entity.cw_adapt_to('IWorkflowable').state in self.entity.PROGRESSING_STATES

    def initial_prevision_date(self):
        return self.entity.prevision_date

    def completion_date(self):
        return self.entity.publication_date or self.entity.prevision_date

    def get_main_task(self):
        return self.entity.project


class Version(AnyEntity):
    __regid__ = 'Version'

    fetch_attrs = ('num', 'description', 'in_state')

    FINISHED_STATES = (u'ready', u'published')
    PROGRESSING_STATES =  (u'dev',)
    PUBLISHED_STATES = (u'published',)

    @classmethod
    def cw_fetch_order(cls, select, attr, var):
        if attr == 'num':
            func = nodes.Function('version_sort_value')
            func.append(nodes.variable_ref(var))
            sterm = nodes.SortTerm(func, asc=False)
            select.add_sort_term(sterm)

    cw_fetch_unrelated_order = cw_fetch_order

    def rest_path(self, use_ext_eid=False):
        return u'%s/%s' % (self.project.rest_path(), self.num)

    @property
    def project(self):
        """ProjectItem interface"""
        return self.version_of[0]

    # dublin core ##############################################################

    def dc_title(self, format='text/plain'):
        return self.num

    def dc_long_title(self):
        return u'%s %s' % (self.project.name, self.num)

    def dc_date(self, date_format=None):
        if self.publication_date:
            date = self.publication_date
        else:
            date = self.modification_date
        return self._cw.format_date(date, date_format=date_format)

    # version'specific logic ###################################################

    def is_published(self):
        return self.cw_adapt_to('IWorkflowable').state in self.PUBLISHED_STATES

    def depends_on_rset(self):
        """return a result set of versions on which this one depends or None"""
        rql = 'DISTINCT Version V WHERE MB done_in MV, MV eid %(x)s, '\
              'MB depends_on B, B done_in V, V version_of P, NOT P eid %(p)s'
        args = {'x': self.eid, 'p': self.project.eid}
        eids = set(str(r[0]) for r in self._cw.execute(rql, args))
        for row in self.related('depends_on'):
            eids.add(str(row[0]))
        if not eids:
            return None
        return self._cw.execute('Version V WHERE V eid in (%s)' % ','.join(eids))

    def next_version(self, states=('planned', 'dev')):
        """return the first version following this one which is in one of the
        given states
        """
        found = False
        for version in reversed(self.project.reverse_version_of):
            if found and (states is None or version.cw_adapt_to('IWorkflowable').state in states):
                return version
            if version is self:
                found = True

    def open_tickets(self):
        return (ticket for ticket in self.reverse_done_in if ticket.is_open())

    def sortvalue(self, rtype=None):
        if rtype is None or rtype == 'num':
            values = []
            for i, part in enumerate(reversed(self.num.split('.'))):
                try:
                    values.append(int(part) * (i * 100))
                except ValueError:
                    values.append(sum(ord(c) * (i * 100) for c in part[:2]))
            return sum(values)
        return super(Version, self).sortvalue(rtype)

    @cached
    def start_date(self):
        """return start date of version, when first transition is done (to
        'dev' state)
        """
        # first tr_info is necessarily the transition to dev
        try:
            tr_info = self.reverse_wf_info_for[1]
            return todate(tr_info.creation_date)
        except IndexError:
            # for versions without transitions passed
            return None

    @cached
    def stop_date(self):
        rql = 'Any MIN(D) WHERE E in_state S, WI wf_info_for E,'\
              'WI to_state S, S name IN ("ready", "published"),'\
              'WI creation_date D, E eid %(x)s'
        rset = self._cw.execute(rql, {'x': self.eid})
        if rset and rset[0][0]:
            return todate(rset[0][0])
        return None


class VersionIUserFriendlyUniqueTogether(IUserFriendlyUniqueTogether):
    __select__ = IUserFriendlyUniqueTogether.__select__ & is_instance('Version')
    def raise_user_exception(self):
        etype, rtypes = self.exc.args
        msg = self._cw._('version %(num)s already exists for project %(project)s') % (
            {'num': self.entity.num, 'project': self.entity.project.name})
        raise ValidationError(self.entity.eid, dict((col, msg) for col in rtypes))
