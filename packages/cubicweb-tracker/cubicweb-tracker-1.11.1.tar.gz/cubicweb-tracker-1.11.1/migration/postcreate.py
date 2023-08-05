"""tracker post creation script, set application's workflows

:organization: Logilab
:copyright: 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubes.localperms import xperm

# Ticket workflow
twf = add_workflow(_('default ticket workflow'), 'Ticket')

created    = twf.add_state(_('created'), initial=True)
inprogress = twf.add_state(_('in-progress'))
closed     = twf.add_state(_('closed'))

twf.add_transition(_('start'), created, inprogress,
                   ('managers', 'staff'), xperm('developer'))
twf.add_transition(_('close'), (created, inprogress,), closed,
                   ('managers', 'staff'), xperm('developer'))

# Version workflow
vwf = add_workflow(_('default version workflow'), 'Version')

planned   = vwf.add_state(_('planned'), initial=True)
dev       = vwf.add_state(_('dev'))
ready     = vwf.add_state(_('ready'))
published = vwf.add_state(_('published'))

vwf.add_transition(_('start development'), planned, dev,
                   ('managers', 'staff'), xperm('developer'))
vwf.add_transition(_('ready'), dev, ready,
                   ('managers', 'staff'), xperm('developer'))
vwf.add_transition(_('publish'), (dev, ready), published,
                   ('managers', 'staff'), xperm('developer'))
vwf.add_transition(_('stop development'), dev, planned,
                   ('managers', 'staff'), xperm('developer'))
