"""Restructured text view to export content of a tracker instance

:organization: Logilab
:copyright: 2007-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.common.textutils import normalize_text

from cubicweb.view import EntityView
from cubicweb.selectors import (is_instance, match_search_state, one_line_rset,
                                multi_lines_rset)
from cubicweb.entity import _marker
from cubicweb.web import action

class ReSTItemView(EntityView):
    __abstract__ = True
    __regid__ = 'docitem'

    title_underline = None # make pylint happy
    templatable = False

    def _title(self, title):
        self.w(u'%s\n%s\n' % (title, self.title_underline*len(title)))

    def paragraph_field(self, entity, attr, **kwargs):
        value = entity.printable_value(attr, format='text/plain', **kwargs)
        if value:
            attrformat = getattr(entity, '%s_format', 'text/plain')
            self.w(u'\n%s\n' % normalize_text(value, 80,
                                              rest=attrformat=='text/rest'))

    def field(self, entity, attr, value=_marker, **kwargs):
        if value is _marker:
            if attr == 'state':
                value = entity.cw_adapt_to('IWorkflowable').printable_state
            else:
                value = entity.printable_value(attr, value, format='text/plain',
                                               **kwargs)
            attr = self._cw._(attr)
        if value:
            self.w(u':%s: %s\n' % (attr, value))

    def entity_call(self, entity):
        """ReST view for Project entities"""
        entity.complete()
        self._title(u'%s %s' % (entity.dc_type(), entity.dc_title()))
        self.render_attributes(entity)
        self.w(u'\n')
        self.render_child(entity)

    # default implementations, override when needed

    def render_title(self, entity):
        self._title(u'%s %s' % (entity.dc_type(), entity.dc_title()))

    fields = ()
    text_fields = ()
    def render_attributes(self, entity):
        for field in self.fields:
            self.field(entity, field, displaytime=False)
        for field in self.text_fields:
            self.paragraph_field(entity, field)

    def render_child(self, entity):
        pass


class ProjectDocumentItemView(ReSTItemView):
    """ReST view for Project entities"""
    __select__ = is_instance('Project')

    title_underline = '='
    fields = ['creation_date']
    text_fields = ['summary', 'description']

    def render_child(self, entity):
        self.wview('docitem', entity.related('version_of', 'object'), 'null')


class VersionDocumentItemView(ReSTItemView):
    """ReST view for Version entities"""
    __select__ = is_instance('Version')

    title_underline = '-'

    def render_title(self, entity):
        self._title(u'%s %s (%s)' % (entity.dc_type(), entity.num,
                                     entity.printable_state))

    def render_attributes(self, entity):
        self.paragraph_field(entity, 'description')
        if entity.cw_adapt_to('IWorkflowable').state == 'published':
            self.field(entity, 'publication_date')
        else:
            self.field(entity, 'prevision_date')

    def render_child(self, entity):
        self.wview('docitem', entity.related('done_in', 'object'), 'null')


class TicketDocumentItemView(ReSTItemView):
    """ReST view for Ticket entities"""
    __select__ = is_instance('Ticket')

    title_underline = '~'
    fields = ['type', 'state']
    text_fields = ['description']

    def render_title(self, entity):
        self._title(u'%s #%s: %s [%s]' % (
            entity.dc_type(), entity.eid, entity.title,
            self._cw._(entity.priority)))


class DocumentView(EntityView):
    __regid__ = 'document'
    __select__ = is_instance('Project', 'Version', 'Ticket')

    title = _('document')
    templatable = False
    content_type = 'text/plain'

    def set_request_content_type(self):
        """overriden to set a .txt filename"""
        self._cw.set_content_type(self.content_type,
                                  filename='cubicwebexport.txt')

    def cell_call(self, row, col):
        self.wview('docitem', self.cw_rset, row=row, col=col)

    def call(self):
        self.w(u'.. -*- coding: %s -*-\n\n' % self._cw.encoding.lower())
        for i in xrange(self.cw_rset.rowcount):
            self.cell_call(row=i, col=0)


# actions ######################################################################

class ProjectVersionExportAction(action.Action):
    __regid__ = 'pvrestexport'
    __select__ = (match_search_state('normal') & one_line_rset() &
                  is_instance('Project', 'Version'))

    title = _('ReST export')
    order = 410

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid='document')


class TicketRESTExportAction(action.Action):
    __regid__ = 'ticketrestexport'
    __select__ = (match_search_state('normal') & multi_lines_rset() &
                  is_instance('Ticket'))
    title = _('ReST export')

    def url(self):
        return self._cw.build_url('view', rql=self.cw_rset.printable_rql(),
                                  vid='document')
