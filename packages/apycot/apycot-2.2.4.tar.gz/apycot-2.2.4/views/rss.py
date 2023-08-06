from logilab.mtconverter import xml_escape

from cubicweb.web import component
from cubicweb.web.views.xmlrss import RSSItemView, RSSView
from cubicweb.selectors import is_instance

from cubes.apycot.views.testexecution import ChecksDescriptorMixin

class TEChangeRSSView(RSSView):
    __regid__ = 'changes_rss'
    __select__ = RSSView.__select__ & is_instance('TestExecution')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        if entity.endtime is not None and entity.status_changes():
            self.wview('changes_rssitem', self.cw_rset, row=row, col=col)


class TERSSItemView(RSSItemView, ChecksDescriptorMixin):
    __select__ = RSSItemView.__select__ & is_instance('TestExecution')

    changes_only = False

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        self.w(u'<item>\n')
        self.w(u'<guid isPermaLink="true">%s</guid>\n'
               % xml_escape(entity.absolute_url()))
        self.render_title_link(entity)
        self.render_description(entity)
        self._marker('dc:date', entity.dc_date(self.date_format))
        self.render_entity_creator(entity)
        self.w(u'</item>\n')

    def render_title_link(self, entity):
        data = {
            'config': entity.configuration.dc_title(),
            'branch': entity.branch,
            'date': entity.printable_value('starttime'),
        }
        title = u"%(config)s #%(branch)s"
        self._marker('title', title % data)

    def render_entity_creator(self, entity):
        self._marker('dc:creator', u'remote execution')

    def render_description(self, entity):
        self.w(u'<description>\n')
        self.describe_execution(entity, changes_only=self.changes_only,
                                xml_compat=True)
        self.w(u'\n</description>\n')


class TEChangeRSSItemView(TERSSItemView):
    __regid__ = 'changes_rssitem'

    changes_only = True


class SubscribeToAllComponent(component.EntityCtxComponent):
    """link to subscribe to rss feed for published versions of project
    """
    __regid__ = 'all_execution_subscribe_rss'
    __select__ = (component.EntityCtxComponent.__select__ &
                  is_instance('TestExecution', 'TestConfig', 'ProjectEnvironment')
                  )
    context = 'ctxtoolbar'
    rss_vid = 'rss'
    order = 110

    def render_body(self, w):
        self._cw.add_css('cubes.apycot.css')
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        label = entity.rss_label(vid=self.rss_vid)
        description = entity.rss_description(vid=self.rss_vid)
        rql = entity.rss_rql(vid=self.rss_vid)
        url = self._cw.build_url('view', vid=self.rss_vid, rql=rql)
        w(u'<a href="%s" title="%s" class="toolbarButton feed_label">%s</a>' % (
            xml_escape(url), xml_escape(description), xml_escape(label)))


class SubscribeToChangeComponent(SubscribeToAllComponent):
    __regid__ = 'changes_execution_subscribe_rss'
    rss_vid = 'changes_rss'
    order = 111
