"""views for Ticket entities

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.view import EntityView, EntityAdapter
from cubicweb.predicates import (objectify_predicate, is_instance, multi_lines_rset,
                                 score_entity)
from cubicweb import tags, uilib
from cubicweb.web import uicfg, component, action
from cubicweb.web.views import primary, baseviews, ibreadcrumbs

_pvs = uicfg.primaryview_section

_pvs.tag_attribute(('Ticket', 'title'), 'hidden')
_pvs.tag_attribute(('Ticket', 'description'), 'attributes')
_pvs.tag_subject_of(('Ticket', 'concerns', '*'), 'hidden')
_pvs.tag_subject_of(('Ticket', 'done_in', '*'), 'attributes')
_pvs.tag_subject_of(('Ticket', 'appeared_in', '*'), 'attributes')
_pvs.tag_subject_of(('Ticket', 'depends_on', '*'), 'sideboxes')
_pvs.tag_object_of(('*', 'depends_on', 'Ticket'), 'sideboxes')

_pvdc = uicfg.primaryview_display_ctrl
_pvdc.tag_attribute(('Ticket', 'description'), {'showlabel': False})


# primary view and tabs ########################################################

class TicketPrimaryView(primary.PrimaryView):
    """primary view for tickets
    """
    __select__ = primary.PrimaryView.__select__ & is_instance('Ticket')

    def render_entity_title(self, entity):
        self._cw.add_css('cubes.tracker.css')
        self.w(u'<h1>%s %s<span class="state"> [%s]</span></h1>'
               % (xml_escape(entity.project.name),
                  xml_escape(entity.dc_title()),
                  xml_escape(self._cw._(entity.cw_adapt_to('IWorkflowable').state))))


# pluggable sections ###########################################################

_pvs.tag_object_of(('*', 'identical_to', 'Ticket'), 'hidden')
_pvs.tag_subject_of(('Ticket', 'identical_to', '*'), 'hidden')

class TicketIdenticalToVComponent(component.RelatedObjectsVComponent):
    """display identical tickets"""
    __regid__ = 'tickectidentical'
    __select__ = component.RelatedObjectsVComponent.__select__ & is_instance('Ticket')

    rtype = 'identical_to'
    target = 'object'

    title = _('Identical tickets')
    context = 'navcontentbottom'
    order = 20


# secondary views ##############################################################

class TicketOneLineView(baseviews.OneLineView):
    """one line representation of a ticket:

    call text view to get link's label, set entity's description on the
    link and display entity's status
    """
    __select__ = is_instance('Ticket')

    def cell_call(self, row, col):
        self.wview('incontext', self.cw_rset, row=row)
        entity = self.cw_rset.get_entity(row, col)
        if entity.in_state:
            self.w(u'&nbsp;[%s]' % xml_escape(self._cw._(entity.cw_adapt_to('IWorkflowable').state)))


class TicketInContextView(baseviews.OneLineView):
    """in-context representation of a ticket:

    call text view to get link's label, set entity's description on the
    link and display entity's status
    """
    __regid__ = 'incontext'
    __select__ = is_instance('Ticket')

    def cell_call(self, row, col):
        self._cw.add_css('cubes.tracker.css')
        entity = self.cw_rset.get_entity(row, col)
        self.w(tags.a(entity.dc_title(), href=entity.absolute_url(),
                      title=uilib.cut(entity.dc_description(), 80),
                      klass=entity.priority))


class StatusSheetTicketView(EntityView):
    __regid__ = 'instatussheet'
    __select__ = is_instance('Ticket')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(tags.div(tags.a('T%s' % entity.eid,
                               href=xml_escape(entity.absolute_url())),
                        title=xml_escape(entity.title),
                        style='display: inline'))

# adapters #####################################################################

class TicketIBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    __select__ = is_instance('Ticket')

    def parent_entity(self):
        parents = self.entity.done_in or self.entity.concerns
        if parents:
            return parents[0]


class IPrevNextAdapter(EntityAdapter):
    """interface for entities which can be linked to a previous and/or next
    entity
    """
    __regid__ = 'IPrevNext'
    __select__ = is_instance('Ticket')

    def previous_entity(self):
        ticket = self.entity
        rql = ('Any X,T ORDERBY X DESC LIMIT 1 '
               'WHERE X is Ticket, X concerns P, X title T, P eid %(p)s, '
               'X eid < %(x)s')
        rset = self._cw.execute(rql, {'p': ticket.project.eid, 'x': ticket.eid})
        if rset:
            return rset.get_entity(0, 0)

    def next_entity(self):
        ticket = self.entity
        rql = ('Any X,T ORDERBY X ASC LIMIT 1 '
               'WHERE X is Ticket, X concerns P, X title T, P eid %(p)s, '
               'X eid > %(x)s')
        rset = self._cw.execute(rql, {'p': ticket.project.eid, 'x': ticket.eid})
        if rset:
            return rset.get_entity(0, 0)


# actions ######################################################################

@objectify_predicate
def ticket_has_next_version(cls, req, rset, row=None, col=0, **kwargs):
    rschema = req.vreg.schema.rschema('done_in')
    if row is None:
        # action is applyable if all entities are ticket from the same project,
        # in an open state, share some versions to which they may be moved
        project, versions = None, set()
        for entity in rset.entities():
            if entity.e_schema != 'Ticket':
                return 0
            if not entity.is_open():
                return 0
            if project is None:
                project = entity.project
            elif project.eid != entity.project.eid:
                return 0
            if entity.in_version():
                if not rschema.has_perm(req, 'delete', fromeid=entity.eid,
                                        toeid=entity.in_version().eid):
                    return 0
                versions.add(entity.in_version().eid)
        if project is None:
            return 0
        maymoveto = []
        for version in project.versions_in_state(('planned', 'dev')).entities():
            if version.eid in versions:
                continue
            for entity in rset.entities():
                if not rschema.has_perm(req, 'add', fromeid=entity.eid,
                                        toeid=version.eid):
                    break
            else:
                maymoveto.append(version)
        if maymoveto:
            rset.maymovetoversions = maymoveto # cache for use in action
            return 1
        return 0
    entity = rset.get_entity(row, 0)
    if entity.in_version() and not rschema.has_perm(
        req, 'delete', fromeid=entity.eid, toeid=entity.in_version().eid):
        return 0
    versionsrset = entity.project.versions_in_state(('planned', 'dev'))
    if not versionsrset:
        return 0
    ticketversion = entity.in_version() and entity.in_version().eid
    maymoveto = [version for version in versionsrset.entities()
                 if not version.eid == ticketversion and
                 rschema.has_perm(req, 'add', fromeid=entity.eid,
                                  toeid=version.eid)]
    if maymoveto:
        rset.maymovetoversions = maymoveto # cache for use in action
        return 1
    return 0


class TicketAction(action.Action):
    __select__ = action.Action.__select__ & is_instance('Ticket')
    # use "mainactions" category to appears in table filter's actions menu
    category = 'mainactions'


class TicketMoveToNextVersionActions(TicketAction):
    __regid__ = 'movetonext'
    __select__ = (TicketAction.__select__
                  & score_entity(lambda x: x.cw_adapt_to('IWorkflowable').state in x.OPEN_STATES)
                  & ticket_has_next_version())

    submenu = _('move to version')

    def fill_menu(self, box, menu):
        # when there is only one item in the sub-menu, replace the sub-menu by
        # item's title prefixed by 'move to version'
        menu.label_prefix = self._cw._(self.submenu)
        super(TicketMoveToNextVersionActions, self).fill_menu(box, menu)

    def actual_actions(self):
        for version in self.cw_rset.maymovetoversions:
            yield self.build_action(version.num, self.url(version))

    def url(self, version):
        if self.cw_row is None:
            eids = [str(row[self.cw_col or 0]) for row in self.cw_rset]
        else:
            eids = [str(self.cw_rset[self.cw_row][self.cw_col or 0])]
        rql = 'SET X done_in V WHERE X eid IN(%s), V eid %%(v)s' % ','.join(eids)
        msg = self._cw._('tickets moved to version %s') % version.num
        return self._cw.user_rql_callback((rql, {'v': version.eid}, 'v'), msg)


class TicketCSVExportAction(TicketAction):
    __regid__ = 'ticketcsvexport'
    __select__ = multi_lines_rset() & TicketAction.__select__

    title = _('csv export')

    def url(self):
        return self._cw.build_url('view', rql=self.cw_rset.printable_rql(),
                              vid='csvexport')
