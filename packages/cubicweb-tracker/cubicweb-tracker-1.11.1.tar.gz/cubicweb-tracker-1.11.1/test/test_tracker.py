"""tracker test application"""

from datetime import date

from cubicweb.devtools.testlib import CubicWebTC, AutomaticWebTest


class AutomaticWebTest(AutomaticWebTest):

    def to_test_etypes(self):
        return set(('Project', 'Ticket', 'Version'))

    def list_startup_views(self):
        return ('stats', 'versionsinfo')

    def post_populate(self, cursor):
        self.commit()
        for version in cursor.execute('Version X').entities():
            version.cw_adapt_to('IWorkflowable').change_state('published')


class VersionCalendarViews(CubicWebTC):
    """specific tests for calendar views"""

    def setup_database(self):
        req = self.request()
        req.create_entity('Version', num=u'0.1.0', publication_date=date(2006, 2, 1))
        req.create_entity('Version', num=u'0.2.0', publication_date=date(2006, 4, 1))
        req.create_entity('Project', name=u"MyProject")
        req.execute('SET V version_of P where V is Version, P is Project')

    def test_calendars_for_versions(self):
        rset = self.execute('Version V')
        for vid in ('onemonthcal', 'oneweekcal'):
            yield self.view, vid, rset, rset.req.reset_headers()

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
