"""entity class for Tag entities

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config

class Tag(AnyEntity):
    """customized class for Tag entities"""
    __regid__ = 'Tag'
    fetch_attrs, cw_fetch_order = fetch_config(['name'])

    def closest_tags_rset(self):
        return self._cw.execute('Any CT, COUNT(X) GROUPBY CT ORDERBY 2 DESC '
                                'LIMIT 5 '
                                'WHERE T tags X, T eid %(x)s, CT tags X, '
                                'NOT CT eid %(x)s', {'x': self.eid})

