"""entity/adapter classes for Folder entities

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.entities.adapters import ITreeAdapter
from cubicweb.predicates import is_instance

class Folder(AnyEntity):
    """customized class for Folder entities"""
    __regid__ = 'Folder'
    fetch_attrs, cw_fetch_order = fetch_config(['name'])


class FolderITreeAdapter(ITreeAdapter):
    __select__ = is_instance('Folder')
    tree_relation = 'filed_under'
