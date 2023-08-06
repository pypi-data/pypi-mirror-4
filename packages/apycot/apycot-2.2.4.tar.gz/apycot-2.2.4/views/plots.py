"""this module contains some plot report views for test execution results

:organization: Logilab
:copyright: 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"
_ = unicode


ERROR_CODES = {
    'error': "#FF5555",
    'failure': "#FF8844",
    'partial': "#FFFF55",
    'success': "#33FF33",
    'other': "#AAAAAA",
    }

from cubicweb.selectors import multi_columns_rset

try:
    from cubes.jqplot.views import JQPlotSimpleView
except ImportError:
    pass
else:
    class JQPlotTestExecutionView(JQPlotSimpleView):
        __regid__ = 'jqplot.testexecution'
        __select__ = multi_columns_rset(3)
        default_renderer = 'bar'

        onload = '''%(id)s = $.jqplot("%(id)s", %(data)s, %(options)s);

        $(document).ready(function(){
            $("#%(id)s").bind('jqplotDataClick',
                function (ev, seriesIndex, pointIndex, data) {
                    /* To open in a NEW window use: */
                    if ( ev.which == 2 ) {
                       window.open(data[2]);
                    } else  {
                       /* To open in the same window use: */
                       window.location.href=data[2];
                    };
                }
            );
        });
        '''
        default_options = {
            'varyBarColor': True,
            'barMargin':0,
            }
        default_legend = {
            'show': False,
            }

        def get_data(self):
            return [[i+1,x[1],self._cw.build_url(x[0])] for i,x in enumerate(self.cw_rset.rows)]

        def set_custom_options(self, options):
            other = ERROR_CODES.get('other')
            options['seriesColors'] = [ERROR_CODES.get(x[2], other) for x in self.cw_rset.rows]
            #FIXME hack to approximate width since it doesn't work in js
            options['series'][0]['rendererOptions']['barWidth'] = 350/len(self.cw_rset.rows)

        def div_holder(self, divid, width, height):
            super(JQPlotTestExecutionView, self).div_holder(divid, width, height)
            self.w(u'''<table class="plotlegend"><tr>%s</tr></table>
            ''' % ''.join(['<td>%s</td><td style="background:%s">&nbsp;&nbsp;&nbsp;</td>' % (x,y) for x,y in  ERROR_CODES.items()]))


def registration_callback(vreg):
    if not 'jqplot' in vreg.config.cubes():
        return # don't register anything from this module
    vreg.register_all(globals().values(), __name__)

