"""tracker web user interface

:organization: Logilab
:copyright: 2006-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.web import uicfg
from cubicweb.web.views import schema
from cubicweb.web.views.urlrewrite import (
    SimpleReqRewriter, SchemaBasedRewriter, rgx, build_rset)


schema.SKIP_TYPES.add('see_also')
schema.ALWAYS_SKIP_TYPES.add('see_also')


def fixed_orderby_rql(sortsdef, asc=True):
    orderby = []
    for rtype, varname in sortsdef:
        if rtype == 'priority':
            orderby.append('priority_sort_value(%s)' % varname)
        elif rtype == 'num':
            orderby.append('version_sort_value(%s)' % varname)
        else:
            orderby.append(varname)
    if asc:
        return 'ORDERBY %s' % ', '.join(orderby)
    return 'ORDERBY %s DESC' % ', '.join(orderby)


class TrackerSimpleReqRewriter(SimpleReqRewriter):
    """handle path with the form::

    versions -> view versions in state ready or development, or marked as
                prioritary.

    foaf.rdf -> view the foaf file for all users
    """
    rules = [
        (rgx('/versions'), dict(vid='versionsinfo')),
        ('/foaf.rdf', dict(vid='foaf', rql='Any X WHERE X is CWUser'))
        ]

class TrackerURLRewriter(SchemaBasedRewriter):
    """handle path with the form::

        project/<name>/tickets           -> view project's tickets
        project/<name>/versions          -> view project's versions in state ready
                                            or development, or marked as
                                            prioritary.
        project/<name>/[version]         -> view version
        project/<name>/[version]/tests   -> test for this version
        project/<name>/[version]/tickets -> tickets for this version
    """
    rules = [
        (rgx('/project/([^/]+)/([^/]+)/tests'),
         build_rset(rql='Version X WHERE X version_of P, P name %(project)s, X num %(num)s',
                    rgxgroups=[('project', 1), ('num', 2)], vid='versiontests')),
        (rgx('/project/([^/]+)/([^/]+)/tickets'),
         build_rset(rql='Any T WHERE T is Ticket, T done_in V, V version_of P, P name %(project)s, V num %(num)s',
                    rgxgroups=[('project', 1), ('num', 2)],
                    vtitle=_('tickets for %(project)s - %(num)s'))),
        (rgx('/project/([^/]+)/versions'),
         build_rset(rql='Any X,N ORDERBY version_sort_value(N) '
                    'WHERE X num N, X version_of P, P name %(project)s, '
                    'EXISTS(X in_state S, S name IN ("dev", "ready")) ',
                    rgxgroups=[('project', 1)], vid='ic_progress_table_view',
                    vtitle=_('upcoming versions for %(project)s'))),
        (rgx('/project/([^/]+)/tickets'),
         build_rset(rql='Any T WHERE T is Ticket, T concerns P, P name %(project)s',
                    rgxgroups=[('project', 1)], vid='table',
                    vtitle=_('tickets for %(project)s'))),
        (rgx('/project/([^/]+)/([^/]+)'),
         build_rset(rql='Version X WHERE X version_of P, P name %(project)s, X num %(num)s',
                    rgxgroups=[('project', 1), ('num', 2)])),
        (rgx('/p/([^/]+)'),
         build_rset(rql='Project P WHERE P name %(project)s',
                    rgxgroups=[('project', 1),])),
        (rgx('/t/([^/]+)'),
         build_rset(rql='Ticket T WHERE T eid %(teid)s',
                    rgxgroups=[('teid', 1),])),
         ]


_pvs = uicfg.primaryview_section
_pvs.tag_object_of(('*', 'todo_by', 'CWUser'), 'relations')

uicfg.primaryview_display_ctrl.tag_object_of(
    ('*', 'todo_by', 'CWUser'),
    {'vid': 'list', 'label': _('working on release(s):'), 'limit': False,
     'filter': lambda rset: rset.filtered_rset(lambda x: x.cw_adapt_to('IWorkflowable').state == u'dev'),
     })

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_subject_of(('*', 'todo_by', '*'), False)
