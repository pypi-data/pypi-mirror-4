"""Specific views for folder entities


:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from cubicweb.utils import UStringIO
from cubicweb.view import EntityView, EntityStartupView
from cubicweb.predicates import (none_rset, is_instance, relation_possible,
                                 score_entity)
from cubicweb.web import uicfg, component
from cubicweb.web.httpcache import GMTOFFSET
from cubicweb.web.views import primary, baseviews
from cubicweb.web.views.treeview import BaseTreeView

def folder_tree(req, done=None):
    """yield folder entities according to the tree structure in a depth search
    prefixed order
    """
    # root folder by default
    rset = req.execute(u'DISTINCT Any T,N,D ORDERBY lower(N) '
                       'WHERE T is Folder, T2 is Folder, NOT T filed_under T2, '
                       'T name N, T description D')
    for root in rset.entities():
        for folder in root.cw_adapt_to('ITree').prefixiter(done):
            yield folder


# form customization ###########################################################

_afs = uicfg.autoform_section
_affk = uicfg.autoform_field_kwargs

_afs.tag_subject_of(('*', 'filed_under', '*'), 'main', 'relations')
_afs.tag_object_of(('*', 'filed_under', '*'), 'main', 'relations')

def subject_filed_under_vocabulary(form, field, limit=None):
    """vocabulary method for the filed_under relation, returning possible
    folders using a tree structure
    """
    entity = form.edited_entity
    if limit is not None and entity.has_eid():
        done = set(x.eid for x in form.edited_entity.filed_under)
    else:
        done = set()
    if entity.has_eid() and entity.__regid__ == 'Folder':
        # on an existant folder entity, don't propose itself and descendants.
        # rely on the prefixiter method to fill the `done` set to do so
        tuple(entity.cw_adapt_to('ITree').prefixiter(done))
    values = sorted((folder.view('combobox'), unicode(folder.eid))
                   for folder in folder_tree(form._cw, done))
    if limit is not None:
        return values[:limit]
    return values
_affk.tag_subject_of(('*', 'filed_under', '*'),
                     {'choices': subject_filed_under_vocabulary})


# folder views ################################################################

_abaa = uicfg.actionbox_appearsin_addmenu
_pvs = uicfg.primaryview_section
_pvdc = uicfg.primaryview_display_ctrl

_abaa.tag_subject_of(('*', 'filed_under', '*'), False)
_abaa.tag_object_of(('*', 'filed_under', '*'), True)
# filed_under displayed by FolderPathBarVComponent
_pvs.tag_subject_of(('*', 'filed_under', '*'), 'hidden')
_pvs.tag_object_of(('*', 'filed_under', '*'), 'hidden')
_pvs.tag_attribute(('Folder', 'name'), 'hidden')
_pvdc.tag_attribute(('Folder', 'description'), {'showlabel': False})

class FolderPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Folder')

    # XXX (syt) useless if we don't activate anymore http caching
    def last_modified(self):
        """return the date/time where this view should be considered as
        modified. Take care of possible related objects modifications.
        """
        entity = self.cw_rset.complete_entity(0)
        try:
            return max([entity.modification_date] +
                       [r.modification_date for r in entity.reverse_filed_under]) + GMTOFFSET
        except TypeError:
            # sqlite bug: UNION queries return date as string :(
            return entity.modification_date

    def render_entity_relations(self, entity):
        itree = entity.cw_adapt_to('ITree')
        self.wview('children', itree.same_type_children(entities=False),
                   'null')
        childrenrset = itree.different_type_children(entities=False)
        if childrenrset:
            self.render_children(childrenrset)

    def render_children(self, rset):
        vid = len(rset.column_types(0)) == 1 and 'sameetypelist' or 'list'
        view = self._cw.vreg['views'].select(vid, self._cw, rset=rset)
        nav_html = UStringIO()
        view.paginate(w=nav_html.write)
        self.w(_(nav_html.getvalue()))
        view.render(w=self.w)
        self.w(_(nav_html.getvalue()))


class FolderChildrenView(EntityView):
    __select__ = is_instance('Folder')
    __regid__ = 'children'
    title = None # should not appears in possible views

    def call(self):
        self.w(u'<div class="navigation">\n')
        self.w(u'<h4>%s</h4>' % self._cw._('subfolders'))
        self.w(u'<div class="subfolders">\n')
        for i in xrange(len(self.cw_rset)):
            self.cell_call(i, 0)
        self.w(u'</div>\n')
        self.w(u'</div>\n')

    def cell_call(self, row, col, klass='folder'):
        self.w(u'<span class="%s">[' % klass)
        self.wview('oneline', self.cw_rset, row=row)
        self.w(u']</span>')


class FolderTreeItemView(baseviews.ListItemView):
    __select__ = is_instance('Folder')
    __regid__ = 'treeitem'

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        # don't filter out subfolder, this generate a much more efficient sql
        # query
        totalrs = self._cw.execute('Any count(X) WHERE X filed_under T, '
                                   'T eid %(x)s', {'x': entity.eid})
        total = totalrs[0][0]
        self.w(u'%s (%s)' % (entity.view('oneline'), total))
        descr = entity.printable_value('description')
        if descr:
            self.w(u'<div>%s</div>' % descr)


class FolderTreeView(BaseTreeView, EntityStartupView):
    """recursive view displaying a folder tree"""
    __select__ = none_rset() | is_instance('Folder')
    title = _('Folder_plural')
    # root folder by default
    default_rql = (u'DISTINCT Any T, lower(N), D ORDERBY lower(N) '
                   'WHERE T is Folder, T2 is Folder, NOT T filed_under T2, '
                   'T name N, T description D')

    def call(self, **kwargs):
        if self.cw_rset is None:
            self.cw_rset = self._cw.execute(self.startup_rql())
        if not self.cw_rset:
            self.w('<h3>%s</h3>' % self._cw._('no folder available'))
        else:
            super(FolderTreeView, self).call(**kwargs)


# folder component ############################################################

class FolderPathBarCtxComponent(component.EntityCtxComponent):
    """parent folder's path bar component

    If an object is related to a folder, display it and its parent folder
    such as: `food > quick > pizza`
    """
    __regid__ = 'folderpathbar'
    __select__ = (component.EntityCtxComponent.__select__
                  & relation_possible('filed_under', 'subject', 'Folder')
                  & score_entity(lambda x: x.filed_under))

    visible = False
    context = 'navtop'
    order = 1

    def render_body(self, w):
        self._cw.view('path', self.entity.related('filed_under'), 'null', w=w,
                      done=set())


# folder box ##################################################################

class FoldersBox(component.RQLCtxComponent):
    """the folder box list root folders"""
    __regid__ = 'folders_box'

    visible = False # disabled by default
    title = _('Folder_plural')
    order = 50
    rql  = ('DISTINCT Any T, lower(N) ORDERBY lower(N) '
            'WHERE T is Folder, T2 is Folder, NOT T filed_under T2, T name N')

    @property
    def treeid(self):
        return '%s_%s_%s' % (self._cw.vreg.config.appid, self.__regid__,
                             self.__class__.__name__.lower())

    def render_body(self, w):
        self._cw.view('treeview', self.cw_rset, subvid='oneline', w=w,
                      treeid=self.treeid)
