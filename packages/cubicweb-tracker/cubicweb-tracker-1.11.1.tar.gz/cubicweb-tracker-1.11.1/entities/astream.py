from cubicweb.selectors import is_instance
from cubes.activitystream.entities import IActivityStreamAdapter, ActivityStreamPart

class TrackerIActivityStreamAdapter(IActivityStreamAdapter):
    __select__ = is_instance('Project', 'Version', 'Ticket')


class ProjectAStreamPart(ActivityStreamPart):
    __select__ = is_instance('Project')
    __regid__ = 'tracker.version'
    rql_parts = (
        'Any TI,TICD,U,TIC WHERE TI is TrInfo, TI creation_date TICD,'
        'TI created_by U?, TI comment TIC, TI wf_info_for T, '
        'T concerns X, X eid %(x)s ',

        'Any T,TCD,U,TT WHERE T creation_date TCD, T created_by U?,'
        'T title TT, T concerns X, X eid %(x)s',

        'Any TI,TICD,U,TIC WHERE TI is TrInfo, TI creation_date TICD,'
        'TI created_by U?, TI comment TIC, TI wf_info_for V, '
        'V version_of X, X eid %(x)s ',

        'Any V,VCD,U,VN WHERE V creation_date VCD, V created_by U?,'
        'V num VN, V version_of X, X eid %(x)s',
        )

class VersionAStreamPart(ActivityStreamPart):
    __select__ = is_instance('Version')
    __regid__ = 'tracker.ticket'
    rql_parts = (
        'Any TI,TICD,U,TIC WHERE TI is TrInfo, TI creation_date TICD,'
        'TI created_by U?, TI comment TIC, TI wf_info_for T, '
        'T done_in X, X eid %(x)s ',

        'Any T,TCD,U,TT WHERE T creation_date TCD, T created_by U?,'
        'T title TT, T done_in X, X eid %(x)s',
        )
