from cubicweb import ValidationError
from cubicweb.predicates import is_instance
from cubicweb.server.hook import match_rtype, Hook

from cubes.folder.entities import Folder

def validate_foldername(session, folder, parent):
    """checks that `folder`'s name doesn't conflict with a sibling folder in
    the parent folder
    """
    for sibling in parent.cw_adapt_to('ITree').children():
        if (isinstance(sibling, Folder)
            and sibling.eid != folder.eid
            and sibling.name == folder.name):
            msg = session._('There is already a sibling folder named %s in the '
                            'parent folder')
            raise ValidationError(folder.eid, {'name': msg % folder.name})


class BeforeAddFiledUnderRelation(Hook):
    """checks that the new folder's name doesn't conflict with
    a sibling folder of the same parent folder
    """
    __regid__ = 'add_file_under_relation_hook'
    events = ('before_add_relation',)
    __select__ = match_rtype('filed_under',)

    def __call__(self):
        session = self._cw
        fromeid = self.eidfrom
        rtype = self.rtype
        toeid = self.eidto
        fromentity = session.entity_from_eid(fromeid)
        if isinstance(fromentity, Folder):
            validate_foldername(session,
                                fromentity,
                                session.entity_from_eid(toeid))


class FolderCreationOrUpdateHook(Hook):
    __regid__ = 'folder_creation_update_hook'
    events = ('after_update_entity',)
    __select__ = is_instance('Folder')

    def __call__(self):
        session = self._cw
        entity = self.entity
        if 'name' not in entity.cw_edited: # was not edited
            return
        try:
            parent = entity.filed_under[0]
        except:
            return # we're root
        validate_foldername(session, entity, parent)
