"""hook to normalize tag names

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.server.hook import Hook
from cubicweb.predicates import is_instance

class AddUpdateTagHook(Hook):
    """ensure tag names are lower case and commas are forbidden"""
    __regid__ = 'add_update_tag'
    __select__ = Hook.__select__ & is_instance('Tag')
    events = ('before_add_entity', 'before_update_entity',)

    def __call__(self):
        if 'name' in self.entity.cw_edited:
            name = self.entity.cw_attr_cache['name'].lower()
            name = ' - '.join(part.strip() for part in name.split(','))
            self.entity.cw_edited['name'] = name
