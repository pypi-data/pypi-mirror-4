"""
:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
_ = unicode

from yams.buildobjs import (EntityType, RelationType, SubjectRelation,
                            String, RichString)
from cubicweb.schema import RRQLExpression

class Folder(EntityType):
    """folders are used to classify entities. They may be defined as a tree.
    """
    name = String(required=True, internationalizable=True,
                  maxsize=64, indexed=True)
    description = RichString(fulltextindexed=True)

    # when using this component, add the X filed_under Folder relation for each
    # type that should be classifiable in folder
    filed_under = SubjectRelation('Folder', description=_('parent folder'))


class filed_under(RelationType):
    """indicates that an entity is classified under a folder"""
    __permissions__ = {
        'read':   ('managers', 'users', 'guests',),
        'add':    ('managers', RRQLExpression('U has_update_permission S'),),
        'delete': ('managers', RRQLExpression('U has_update_permission S'),),
        }
