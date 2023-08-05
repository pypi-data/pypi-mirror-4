"""xml/rdf views for tracker related entities (doap, linked data)

:organization: Logilab
:copyright: 2001-2011 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.view import EntityView
from cubicweb.selectors import is_instance

class LinkedDataView(EntityView):
    __regid__ = 'linked_data'
    __select__ = is_instance('Project')

    title = _('linked data')
    templatable = False
    content_type = 'text/xml'
    item_vid = 'linked_data_item'

    def call(self):
        self.w(u'<?xml version="1.0" encoding="%s"?>\n' % self._cw.encoding)
        self.w(u'''<rdf:RDF
             xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
             xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
             xmlns:owl="http://www.w3.org/2002/07/owl#"
             xmlns:foaf="http://xmlns.com/foaf/0.1/"
             xmlns:doap="http://usefulinc.com/ns/doap#">\n''')
        for i in xrange(self.cw_rset.rowcount):
            self.cell_call(row=i, col=0)
        self.w(u'</rdf:RDF>\n')

    def cell_call(self, row, col):
        self.wview(self.item_vid, self.cw_rset, row=row, col=col)


class LinkedDataProjectItemView(EntityView):
    __regid__ = 'linked_data_item'
    __select__ = is_instance('Project')

    def cell_call(self, row, col):
        '''display all project attribut and project dependencies and external project (in doap format) if
        it is related to'''
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u' <doap:Project rdf:about="%s">\n' % xml_escape(entity.absolute_url()))
        self.common_doap(entity)
        self.w(u' </doap:Project>\n')

    def project_references(self, entity, refattr):
        refs = getattr(entity, refattr)
        if refs:
            self.w(u'<%s>' % refattr)
            for ref in refs:
                self.w(u'<doap:Project rdf:resource="%s"/>'% xml_escape(ref.absolute_url()))
            self.w(u'</%s>' % refattr)

    def common_doap(self, entity):
        self.w(u'  <doap:name>%s</doap:name>\n'% xml_escape(entity.dc_title()))
        self.w(u'  <doap:created>%s</doap:created>\n' % (entity.creation_date.strftime('%Y-%m-%d')))
        if entity.summary:
            self.w(u'  <doap:shortdesc>%s</doap:shortdesc>\n' % xml_escape(entity.summary))
        descr = entity.printable_value('description', format='text/plain')
        if descr:
            self.w(u'  <doap:description>%s</doap:description>\n' % xml_escape(descr))



class ProjectDoapItemView(LinkedDataProjectItemView):
    __regid__ = 'doapitem'
    __select__ = is_instance('Project')

    def cell_call(self, row, col):
        """ element as an item for an doap description """
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<doap:Project rdf:about="%s">\n' % xml_escape(entity.absolute_url()))
        self.common_doap(entity)
        # version
        ver = entity.latest_version()
        if ver:
            self.w(u'  <doap:release>\n')
            ver.view('doapitem', w=self.w)
            self.w(u'  </doap:release>\n')
        # repository
        self.w(u'</doap:Project>\n')


class VersionDoapItemView(EntityView):
    __regid__ = 'doapitem'
    __select__ = is_instance('Version')

    def cell_call(self, row, col):
        """ element as an item for an doap description """
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<doap:Version>\n')
        self.w(u'  <doap:revision>%s</doap:revision>\n' % xml_escape(entity.num) )
        self.w(u'  <doap:created>%s</doap:created>\n' % entity.dc_date('%Y-%m-%d'))
        self.w(u'</doap:Version>\n')


class DoapView(LinkedDataView):
    __regid__ = 'doap'
    title = _('doap')
    item_vid = 'doapitem'
    __select__ = is_instance('Project', 'Version')



