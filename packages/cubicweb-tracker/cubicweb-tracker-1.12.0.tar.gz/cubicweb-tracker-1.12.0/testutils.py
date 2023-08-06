"""some utilities for testing tracker security

:organization: Logilab
:copyright: 2008-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

from __future__ import with_statement

__docformat__ = "restructuredtext en"


from itertools import repeat

from logilab.common.decorators import cached

from cubicweb import Unauthorized, ValidationError
from cubicweb.devtools import (BaseApptestConfiguration, TestServerConfiguration,
                               get_test_db_handler)
from cubicweb.devtools.testlib import CubicWebTC

def create_project_rql(pname, description=None):
    return 'INSERT Project X: X name %(name)s, X description %(descr)s', \
           {'name': unicode(pname), 'descr': unicode(description)}

def create_version_rql(num, pname):
    return 'INSERT Version X: X num %(num)s, X version_of P '\
           'WHERE P name %(name)s', \
           {'num': unicode(num), 'name': unicode(pname)}

def create_ticket_rql(title, pname):
    return 'INSERT Ticket X: X title %(title)s, X concerns P '\
           'WHERE P name %(name)s', \
           {'title': unicode(title), 'name': unicode(pname)}


# XXX take both TestCase *class* and session (need for both since session only
# available on TestCase *instance*)
def security_tc_init_project(tc, session, name, user_prefix=None):
    project = session.execute(*create_project_rql(name)).get_entity(0, 0)
    if user_prefix is None:
        user_prefix = name
    for perm in (u'developer', u'client'):
        group = "%s%ss" % (name, perm)
        session.create_entity('CWGroup', name=group)
        tc.grant_permission(session, project, group, perm)
        tc.create_user(session, '%s%s' % (user_prefix, perm), groups=('users', group,),
                       commit=False)
    return project


class TrackerTCMixIn(object):

    def create_project(self, pname, description=None):
        return self.execute(*create_project_rql(pname, description))

    def create_version(self, num, pname='cubicweb'):
        return self.execute(*create_version_rql(num, pname))

    def create_ticket(self, title, vnum=None, pname='cubicweb'):
        rset = self.execute(*create_ticket_rql(title, pname))
        if vnum:
            self.execute('SET X done_in V WHERE X eid %(x)s, V num %(num)s',
                         {'x': rset[0][0], 'num': vnum})
        return rset


class TrackerBaseTC(TrackerTCMixIn, CubicWebTC):
    def setup_database(self):
        self.cubicweb = self.request().create_entity('Project', name=u'cubicweb',
                                        description=u"cubicweb c'est beau")

    def tearDown(self):
        CubicWebTC.tearDown(self)
        for sessionid in list(self.repo._sessions):
            self.repo.close(sessionid)


class SecurityTC(TrackerTCMixIn, CubicWebTC):
    repo_config = BaseApptestConfiguration('data')
    def setUp(self):
        """
            User created:
                - stduser
                - staffuser
                - prj1developer
                - prj1client
                - prj2developer
                - prj2client
        """
        CubicWebTC.setUp(self)
        self.__cnxs = {'admin': self.cnx}
        self.create_user(self.session, 'stduser')
        self.create_user(self.session, 'staffuser', groups=('users', 'staff',))
        self.cubicweb = security_tc_init_project(self, self.session, 'cubicweb', user_prefix='prj1')
        self.project2 = security_tc_init_project(self, self.session, 'project2', user_prefix='prj2')
        self.commit()
        self.maxeid = self.execute('Any MAX(X)')[0][0]

    def tearDown(self):
        CubicWebTC.tearDown(self)
        for sessionid in list(self.repo._sessions):
            self.repo.close(sessionid)

    def mylogin(self, user, **kwargs):
        if not user in self.__cnxs:
            if user == 'narval':
                kwargs['password'] = 'narval0'
            self.__cnxs[user] = self.login(user, autoclose=False, **kwargs)
        return self.__cnxs[user]

    def restore_connection(self):
        # overridden so current connection isn't closed, which is unexpected
        # with `mylogin`
        cnx, self.websession = self._orig_cnx
        self.set_cnx(cnx)

    def _test_tr_fail(self, user, x, trname):
        cnx = self.mylogin(user)
        try:
            entity = cnx.request().entity_from_eid(x)
            # if the user can't see entity x, Unauthorized is raised, else if he
            # can't pass the transition, Validation is raised
            self.assertRaises((Unauthorized, ValidationError),
                              entity.cw_adapt_to('IWorkflowable').fire_transition, trname)
        finally:
            cnx.rollback()

    def _test_tr_success(self, user, x, trname):
        cnx = self.mylogin(user)
        try:
            entity = cnx.request().entity_from_eid(x)
            entity.cw_adapt_to('IWorkflowable').fire_transition(trname)
            cnx.commit()
        except:
            cnx.rollback()
            raise

#from unittest_querier_planner import do_monkey_patch, undo_monkey_patch


class ExternalSourceConfiguration(TestServerConfiguration):
    @cached
    def sources(self):
        res = {'admin': {'login': 'admin', 'password': 'gingkow'}}
        res['system'] = {'adapter':     'native',
                         'db-driver':   'sqlite',
                         'db-name':     'tmpdb-extern',
                         'db-encoding': 'utf8',
                         'db-host':     '',
                         'db-user':     'admin',
                         'db-password': 'gingkow',
                         }
        return res

class External2SourceConfiguration(TestServerConfiguration):
    @cached
    def sources(self):
        res = {'admin': {'login': 'admin', 'password': 'gingkow'}}
        res['system'] = {'adapter':     'native',
                         'db-driver':   'sqlite',
                         'db-name':     'tmpdb-extern2',
                         'db-encoding': 'utf8',
                         'db-host':     '',
                         'db-user':     'admin',
                         'db-password': 'gingkow',
                         }
        return res

def ms_test_init(apphome):
    handler = get_test_db_handler(ExternalSourceConfiguration(
        'data2', apphome=apphome))
    handler.build_db_cache()
    repo2, cnx2 = handler.get_repo_and_cnx()
    cu = cnx2.cursor()
    ep1eid = cu.execute('INSERT Project X: X name "Extern project 1"')[0][0]
    ep1v1eid = cu.execute('INSERT Version V: V num "0.1.0", V version_of X WHERE X name "Extern project 1"')[0][0]
    ep2eid = cu.execute('INSERT Project X: X name "Extern project 2"')[0][0]
    ep2v1eid = cu.execute('INSERT Version V: V num "0.1.0", V version_of X WHERE X name "Extern project 2"')[0][0]
    cnx2.commit()

    handler = get_test_db_handler(External2SourceConfiguration(
        'data3', apphome=apphome))
    handler.build_db_cache()
    repo3, cnx3 = handler.get_repo_and_cnx()
    cu3 = cnx3.cursor()
    e2p1eid = cu3.execute('INSERT Project X: X name "Extern2 project 1"')[0][0]
    cnx3.commit()

    # XXX, access existing connection, no pyro connection
    from cubicweb.server.sources.pyrorql import PyroRQLSource
    PyroRQLSource.get_connection = lambda x: x.uri == 'extern' and cnx2 or cnx3
    # necessary since the repository is closing its initial connections pool though
    # we want to keep cnx2 valid
    from cubicweb.dbapi import Connection
    Connection.close = lambda x: None

    eids = {'ep1eid': ep1eid,
            'ep1v1eid': ep1v1eid,
            'ep2eid': ep2eid,
            'ep2v1eid': ep2v1eid,
            'e2p1eid': e2p1eid
            }
    return repo2, cnx2, repo3, cnx3, eids


class BaseMSTC(CubicWebTC):

    def setup_database(self):
        req = self.request()
        mapping = zip(('Project', 'Version', 'State',
                       'in_state', 'subproject_of',
                       'version_of',
                       'done_in', 'concerns', # XXX Ticket not supported...
                       ),
                      repeat(u'write'))
        mapping.append( ('state_of', u'dontcross') )
        for uri, config in [(u'extern', u'''
cubicweb-user=admin
cubicweb-password=gingkow'''),
                            (u'extern2', u'''
cubicweb-user=admin
cubicweb-password=gingkow''')]:
            source = req.create_entity('CWSource', name=unicode(uri),
                                       type=u'pyrorql',
                                       config=unicode(config))
            self.commit()
            source.init_mapping(mapping)
            self.commit()

    def setUp(self):
        CubicWebTC.setUp(self)
        self.extern = self.repo.sources_by_uri['extern']
        # trigger import from external source since sqlite doesn't support
        # concurrent access to the database
        self.execute('Any P, V WHERE V? version_of P')
        self.execute('State X')
        self.ip1eid = self.execute('INSERT Project X: X name "Intern project 1"')[0][0]
        self.ip1v1eid = self.execute('INSERT Version V: V num "0.1.0", V version_of X WHERE X name "Intern project 1"')[0][0]
        self.ip1t1eid = self.execute('INSERT Ticket X: X title "ticket project 1", X concerns P, X done_in V WHERE P eid %(p)s, V eid %(v)s',
                                     {'p': self.ip1eid, 'v': self.ip1v1eid})[0][0]
        self.ip2eid = self.execute('INSERT Project X: X name "Intern project 2"')[0][0]
        self.ip2v1eid = self.execute('INSERT Version V: V num "0.1.0", V version_of X WHERE X name "Intern project 2"')[0][0]
        self.ip2t1eid = self.execute('INSERT Ticket X: X title "ticket project 2", X concerns P, X done_in V, X depends_on T WHERE P eid %(p)s, V eid %(v)s, T eid %(t)s',
                                     {'p': self.ip2eid, 'v': self.ip2v1eid, 't': self.ip1t1eid})[0][0]
        self.ip3eid = self.execute('INSERT Project X: X name "Intern project 3"')[0][0]
        self.commit()

    def tearDown(self):
        for source in self.repo.sources[1:]:
            self.repo.remove_source(source.uri)
        CubicWebTC.tearDown(self)
        for sessionid in list(self.repo._sessions):
            self.repo.close(sessionid)

    def extid2eid(self, extid, etype):
        return self.repo.extid2eid(self.extern, str(extid), etype, self.session)

    def fire_transition(self, eid, trname):
        e = self.execute('Any X WHERE X eid %(x)s', {'x': eid}).get_entity(0, 0)
        e.cw_adapt_to('IWorkflowable').fire_transition(trname)

    def change_state(self, eid, stname):
        e = self.execute('Any X WHERE X eid %(x)s', {'x': eid}).get_entity(0, 0)
        e.cw_adapt_to('IWorkflowable').change_state(stname)

