"""Specific views for tag

:organization: Logilab
:copyright: 2003-2011 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb.predicates import (match_kwargs, match_form_params,
                                 match_user_groups,
                                 has_related_entities, one_etype_rset,
                                 is_instance, relation_possible)
from cubicweb import uilib, tags
from cubicweb.web import uicfg, stdmsgs, component, box, facet
from cubicweb.web.views import baseviews, ajaxcontroller, xmlrss


_afs = uicfg.autoform_section
_afs.tag_subject_of(('*', 'tags', '*'), formtype='main', section='hidden')
_afs.tag_object_of(('*', 'tags', '*'), formtype='main', section='hidden')

# relations displayed by some component or box below, don't display them in
# primary view
_pvs = uicfg.primaryview_section
_pvs.tag_subject_of(('*', 'tags', '*'), 'hidden')
_pvs.tag_object_of(('*', 'tags', '*'), 'hidden')
_pvs.tag_subject_of(('Tag', 'tags', '*'), 'relations')
_pvs.tag_attribute(('Tag', 'name'), 'hidden')


class TagInContextView(baseviews.InContextView):
    __regid__ = 'incontext'
    __select__ = is_instance('Tag')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(tags.a(entity.view('textincontext'), href=entity.absolute_url(),
                      title=uilib.cut(entity.dc_description(), 50), rel=u'tag'))


class TagCloudView(baseviews.OneLineView):
    """cloud view to make a link on tagged entities appearing more or less big
    according to the number of tagged entities

    expect a result set with tag eid in the first column and number of tagged
    objects in the second column.
    expect as well:
    * `maxsize` argument, the maximum number of tagged entities by a tag in the
      cloud
    * `etype` argument, the entity type we are filtering
    """
    __regid__ = 'tagcloud'
    __select__ = is_instance('Tag') & (match_kwargs('etype')
                                      | match_form_params('etype'))

    need_navigation = False
    add_div_section = False # configure View.call behaviour

    onload_js = '''
jQuery(document).tagcloud.defaults = {
  size: {start: 0.8, end: 2.5, unit: "em"},
  color: {start: "#333", end: "#FF7700"}
};
jQuery("#tagcloud a").tagcloud();
'''
    def call(self, *args, **kwargs):
        self._cw.add_js('jquery.tagcloud.js')
        self._cw.html_headers.add_onload(self.onload_js)
        self.w(u'<div id="tagcloud">')
        super(TagCloudView, self).call(*args, **kwargs)
        self.w(u'</div>')

    def cell_call(self, row, col, etype=None, **kwargs):
        if etype is None:
            etype = self._cw.form['etype']
        entity = self.cw_rset.get_entity(row, col)
        mysize = self.cw_rset[row][1]
        # generate url according to where it is called from eg. when browsing
        # blogs the tag box should point to Blogs tagged by...
        rql = 'Any X WHERE T tags X, T eid %s, X is %s' % (entity.eid, etype)
        # XXX rel=mysize, can't we set rel='tag %s' % mysize to get back the
        #     'tag' rel?
        self.w(tags.a(entity.name, rel=mysize,
                      href=self._cw.build_url('view', rql=rql))+ u' ')


# simple boxes #################################################################

class ClosestTagsBox(component.EntityCtxComponent):
    __regid__ = 'closest_tags_box'
    __select__ = component.EntityCtxComponent.__select__ & is_instance('Tag',)
    order = 25
    title = _('closest tags')

    def init_rendering(self):
        self.closest_tags = self.entity.closest_tags_rset()
        if not self.closest_tags:
            raise component.EmptyComponent()

    def render_body(self, w):
        self._cw.view('incontext', self.closest_tags, w=w)


class SimilarityBox(component.EntityCtxComponent):
    """layout closest entities (ie. entities that share tags)"""
    __regid__ = 'similarity_box'
    __select__ = (component.EntityCtxComponent.__select__
                  & has_related_entities('tags', 'object', 'Tag'))
    order = 21
    rql = ('Any Y,COUNT(T) GROUPBY Y ORDERBY 2 DESC %s '
           'WHERE X eid %%(x)s, T tags X, T tags Y, NOT Y eid %%(x)s')

    def init_rendering(self):
        self.cw_rset = self._cw.execute(self.rql % ('LIMIT 5'),
                                        {'x': self.entity.eid})
        if not self.cw_rset:
            raise component.EmptyComponent()

    def render_title(self, w):
        if self.cw_rset.rowcount == 1:
            w(self._cw._('similar entity'))
        else:
            w(self._cw._('similar entities'))

    def render_body(self, w):
        self._cw.view('outofcontext', self.cw_rset, w=w)
        rql = self.rql % '' % {'x': self.entity.eid}
        title = self._cw._('entities similar to %s') % self.entity.dc_title()
        url = self._cw.build_url('view', rql=rql,
                                 vtitle=title)
        w(u'<div>[%s]</div>' % tags.a(self._cw._('see all'), href=url))


class TagsCloudBox(component.CtxComponent):
    """display a box with tag cloud for """
    __regid__ = 'tagcloud_box'
    __select__ = (component.CtxComponent.__select__ & one_etype_rset() &
                  relation_possible('tags', 'object', 'Tag'))

    visible = False # disabled by default
    order = 30
    title = _('Tag_plural')
    context = 'left'

    def init_rendering(self):
        self.etype = iter(self.cw_rset.column_types(0)).next()
        self.cw_rset = self._cw.execute(
            'Any T,COUNT(X),TN GROUPBY T,TN LIMIT 30'
            'WHERE X is %s, T tags X, T name TN' % self.etype)
        if not self.cw_rset:
            raise component.EmptyComponent()

    def render_body(self, w):
        self._cw.view('tagcloud', self.cw_rset, etype=self.etype, w=w)
        rql = ('Any T,COUNT(X),TN GROUPBY T,TN '
               'WHERE X is %s, T tags X, T name TN' % self.etype)
        url = xml_escape(self._cw.build_url(rql=rql, vid='tagcloud', etype=self.etype))
        w(u'<div>[%s]</div>' % tags.a(self._cw._('see all tags'), href=url))


# the tags box #################################################################

class TagsBox(component.AjaxEditRelationCtxComponent):
    """the tag box: control tag of taggeable entity providing an easy way to
    add/remove tag
    """
    __regid__ = 'tags_box'

    rtype = 'tags'
    role = 'object'
    target_etype = 'Tag'

    order = 20

    added_msg = _('entity has been tagged')
    removed_msg = _('tag has been removed')

    fname_vocabulary = 'unrelated_tags'
    fname_validate = 'tag_entity'
    fname_remove = 'untag_entity'


@ajaxcontroller.ajaxfunc(output_type='json')
def unrelated_tags(self, eid):

    """return tag unrelated to an entity"""
    rql = 'Any N ORDERBY N WHERE T is Tag, T name N, NOT T tags X, X eid %(x)s'
    return [name for (name,) in self._cw.execute(rql, {'x' : eid})]


@ajaxcontroller.ajaxfunc
def tag_entity(self, eid, taglist):
    execute = self._cw.execute
    # get list of tag for this entity
    tagged_by = set(tagname for (tagname,) in
                    execute('Any N WHERE T name N, T tags X, X eid %(x)s',
                            {'x': eid}))
    for tagname in taglist:
        tagname = tagname.strip()
        if not tagname or tagname in tagged_by:
            continue
        tagrset = execute('Tag T WHERE T name %(name)s', {'name': tagname})
        if tagrset:
            rql = 'SET T tags X WHERE T eid %(t)s, X eid %(x)s'
            execute(rql, {'t': tagrset[0][0], 'x' : eid})
        else:
            rql = 'INSERT Tag T: T name %(name)s, T tags X WHERE X eid %(x)s'
            execute(rql, {'name' : tagname, 'x' : eid})

@ajaxcontroller.ajaxfunc
def untag_entity(self, eid, tageid):
    rql = 'DELETE T tags X WHERE T eid %(t)s, X eid %(x)s'
    self._cw.execute(rql, {'t': tageid, 'x' : eid})


# the merge tags component #####################################################

class MergeComponent(component.EntityCtxComponent):
    __regid__ = 'mergetag'
    __select__ = (component.EntityCtxComponent.__select__ &
                  is_instance('Tag') & match_user_groups('managers'))
    context = 'navcontentbottom'
    title = _('merge tags')

    def render_body(self, w):
        self._cw.add_js(('cubes.tag.merge.js', 'cubicweb.widgets.js'))
        entity = self.entity
        w(u'<div id="tagmergeformholder%s">' % entity.eid)
        w(u'<h5>%s</h5>' % self._cw._('Enter a tag name'))
        w(u'<input  type="hidden" id="tageid" value="%s"/>' % entity.eid)
        w(u'<input id="acmergetag" type="text" class="widget" cubicweb:dataurl="%s" '
          u'cubicweb:loadtype="auto" cubicweb:wdgtype="RestrictedSuggestField" />'
          % xml_escape(self._cw.build_url('json', fname='unrelated_merge_tags',
                                          arg=entity.eid)))
        w(u'<div id="tagged_entities_holder"></div>')
        w(u'<div id="sgformbuttons" class="hidden">')
        w(u'<input class="validateButton" type="button" value="%s" onclick="javascript:mergeTags(%s);"/>'
               % ( self._cw._('merge (keeping %s)') % xml_escape(entity.dc_title()), entity.eid))
        w(u'<input class="validateButton" type="button" value="%s" onclick="javascript:cancelSelectedMergeTag(%s)"/>'
               % ( self._cw._(stdmsgs.BUTTON_CANCEL[0]), entity.eid))
        w(u'</div>')
        w(u'</div>')


@ajaxcontroller.ajaxfunc(output_type='json')
def unrelated_merge_tags(self, eid):
    """return tag unrelated to an entity"""
    rql = 'Any N ORDERBY N WHERE T is Tag, T name N, NOT T eid %(x)s'
    return [name for (name,) in self._cw.execute(rql, {'x' : eid})]

@ajaxcontroller.ajaxfunc(output_type='xhtml')
def tagged_entity_html(self, name):
    rset = self._cw.execute('Any X ORDERBY X DESC LIMIT 10 WHERE T tags X, '
                            'T name %(x)s', {'x': name})
    html = []
    if rset:
        html.append('<div id="taggedEntities">')
        #FIXME - add test to go through select_view
        view = self._cw.vreg['views'].select('list', self._cw, rset=rset)
        html.append(view.render(title=self._cw._('linked entities:')))
        html.append(u'</div>')
        # html.append(self._cw.view('list', rset))
    else:
        html.append('<div>%s</div>' %_('no entities related to this tag'))
        view = self._cw.vreg['views'].select('null', self._cw, rset=rset)
    return u' '.join(html)


@ajaxcontroller.ajaxfunc(output_type='xhtml')
def merge_tags(self, eid, mergetag_name):
    mergetag_name = mergetag_name.strip(',') # XXX
    self._cw.execute('SET T tags X WHERE T1 tags X, NOT T tags X, '
                     'T eid %(x)s, T1 name %(name)s',
                     {'x': eid, 'name': mergetag_name})
    self._cw.execute('DELETE Tag T WHERE T name %(name)s', {'name': mergetag_name})
    #FIXME - add test to go through select_view
    view = self._cw.vreg['views'].select('primary', self._cw, 
                                         rset=self._cw.eid_rset(eid))
    return view.render()


# facets, ui adapter ###########################################################

class TagsFacet(facet.RelationFacet):
    __regid__ = 'tags-facet'
    rtype = 'tags'
    role = 'object'
    target_attr = 'name'


class TagIFeedAdapter(xmlrss.IFeedAdapter):
    __select__ = is_instance('Tag')

    def rss_feed_url(self):
        rql = ('Any X ORDERBY CD DESC LIMIT 15 WHERE '
               'T tags X, T eid %s, X modification_date CD') % self.entity.eid
        return self._cw.build_url(rql=rql, vid='rss', vtitle=self.entity.dc_title())
