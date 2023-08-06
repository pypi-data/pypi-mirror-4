"""company related views in company package

:organization: Logilab
:copyright: 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter import xml_escape

from cubicweb.view import EntityView
from cubicweb.predicates import is_instance
from cubicweb.web import uicfg
from cubicweb.web.views import primary

_afs = uicfg.autoform_section
_afs.tag_subject_of(('*', 'phone', '*'), 'main', 'inlined')
_afs.tag_subject_of(('*', 'headquarters', '*'), 'main', 'inlined')

_abaa = uicfg.actionbox_appearsin_addmenu
_abaa.tag_object_of(('*', 'subsidiary_of', 'Company'), True)
_abaa.tag_subject_of(('Company', 'is_part_of', '*'), True)

_pvs = uicfg.primaryview_section
_pvs.tag_attribute(('Company', 'rncs'), 'hidden') # siren
_pvs.tag_attribute(('Company', 'name'), 'hidden')
_pvs.tag_attribute(('Company', 'web'), 'hidden')
_pvs.tag_subject_of(('Company', 'headquarters', '*'), 'hidden')
_pvs.tag_subject_of(('Company', 'phone', '*'), 'hidden')
_pvs.tag_subject_of(('Company', 'use_email', '*'), 'hidden')
_pvs.tag_subject_of(('*', 'subsidiary_of', '*'), 'relations')
_pvs.tag_object_of(('*', 'subsidiary_of', '*'), 'relations')


class CompanyPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Company')

    attr_table_relations = [('phone', ', '.join),
                            ('use_email', ', '.join),
                            ('headquarters', '<hr/>\n'.join),
                            ('web', None),
                            ]

    def render_entity_attributes(self, entity):
        super(CompanyPrimaryView, self).render_entity_attributes(entity)
        hascontent = False
        for rel, join in self.attr_table_relations:
            if join is None:
                val = entity.printable_value(rel)
            else:
                val = join(e.view('incontext') for e in getattr(entity, rel, ()))
            if val:
                if not hascontent:
                    self.w(u"<table>")
                    hascontent = True
                self.field(rel, val, table=True)
        if hascontent:
            self.w(u"</table>")


class CompanyAddressView(EntityView):
    __regid__ = 'address_view'
    __select__ = is_instance('Company')
    title = None

    def cell_call(self, row, col, incontext=False):
        """only prints address"""
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<div class="vcard">')
        if not incontext:
            self.w(u'<h3><a class="fn org url" href="%s">%s</a></h3>'
                   % (xml_escape(entity.absolute_url()), xml_escape(entity.name)))
        self.wview('incontext',entity.related('headquarters'), 'null')
        if entity.web :
            url = xml_escape(entity.web)
            self.w(u"<a href='%s'>%s</a><br/>" % (url, url))
        self.wview('list', entity.related('phone'),'null')
        self.wview('list', entity.related('use_email'),'null')
        self.w(u'</div>')


