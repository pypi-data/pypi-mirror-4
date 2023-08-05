# copyright 2011-2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.
"""basic plot views based on jqplot (http://www.jqplot.com)
"""

__docformat__ = "restructuredtext en"
_ = unicode

from logilab.common.date import datetime2ticks
from logilab.mtconverter import xml_escape

from cubicweb import NoSelectableObject
from cubicweb.view import AnyRsetView
from cubicweb.utils import json_dumps, JSString, js_dumps
from cubicweb.selectors import multi_columns_rset, match_kwargs

def filterout_nulls(abscissa, plot):
    filtered = []
    for x, y in zip(abscissa, plot):
        if x is None or y is None:
            continue
        filtered.append( (x, y) )
    return sorted(filtered)


class JQPlotRsetView(AnyRsetView):
    """default view to render a JQPlot graph, extracting series from rset on
    which this view is applied.

    Rendering allows many arguments. `JQPlot.plot` options:

    * `series_options`: JQPlot's `series`
    * `series_defaults`: JQPlot's `seriesDefaults`
    * `axes_defaults`: JQPlot's `axesDefaults`
    * `axes`, `legend`, `cursor`, `highlighter`, `title`: eponym in JQPlot
    * `extra`: optional dictionary that will be added to `plot` options
    * `cursor`: either explicit dictionary giving jqplot options, or True to
      get `default_cursor`

    `series_default`, `axes_default`, `legend`, `axes`, `highlighter`
    and `extra` will use `default_<argname>` class attribute as default value if
    not specified (ie None). You may want to change those class attributes to
    make site wide changes to your plots.

    Other allowed arguments:

    * `divid`: DOM id of the plot node in the document. The plot will also be
      available as a javascript global variable of the same name (hence it
      should be a valid js identifier when specified).

    * `width`, `height`: graph width and height. If an int is given, px expected.

    * `displayfilter`: boolean flag telling if filter form should be displayed
       (False by default)

    * `mainvar`: if filter is displayed, optional name in the RQL query
      indicating the filtered variable (variable in the first column by default)

    * `displayactions`: boolean flag telling if plot actions should be displayed
      (False by default)

    * `actions`: if actions are displayed, may be used to control displayed
      actions. By default, use `ACTIONS` class attribute.
    """
    __regid__ = 'jqplot.default'
    __select__ = multi_columns_rset() & match_kwargs('series_options')

    onload = 'cw.cubes.jqplot.buildPlot("%(id)s", %(data)s, %(jqplotArgs)s);'

    # default values in above jqplotArgs (remove 'default_' and turn to camel
    # case to get jqplot argument name
    default_series_defaults = {
        'rendererOptions': {'fillToZero': True},
        }
    default_axes_defaults = {
        'useSeriesColor': True,
        }
    default_legend = {
        'show': True,
        'placement': 'outsideGrid',
        }
    default_axes = {
        'xaxis': {'autoscale': True},
        }
    default_cursor = {
        'show': True,
        'zoom': True,
        'showTooltip': True,
        }
    default_highlighter = {
        'show': True,
        'sizeAdjust': 7.5,
        }
    default_extra = {}

    # symbolic names easing configuration of [curve|axis|tick] renderers
    renderers = {
        'bar': (JSString('$.jqplot.BarRenderer'),
                #'plugins/jqplot.barRenderer.min.js'),
                # use non-min version because we patched the javascript
                'plugins/jqplot.barRenderer.js'),
        'pie': (JSString('$.jqplot.PieRenderer'),
                'plugins/jqplot.pieRenderer.min.js'),
        'donut': (JSString('$.jqplot.DonutRenderer'),
                  'plugins/jqplot.donutRenderer.min.js'),
        'ohlc': (JSString('$.jqplot.OHLCRenderer'),
                 'plugins/jqplot.ohlcRenderer.js'),
        }
    axis_renderers = {
        'linear': (JSString('$.jqplot.LinearAxisRenderer'), None),
        'date': (JSString('$.jqplot.DateAxisRenderer'),
                 'plugins/jqplot.dateAxisRenderer.min.js'),
        'category': (JSString('$.jqplot.CategoryAxisRenderer'),
                     'plugins/jqplot.categoryAxisRenderer.min.js'),
        }
    tick_renderers = {
        'tick': (JSString('$.jqplot.CanvasAxisTickRenderer'),
                 ['plugins/jqplot.canvasTextRenderer.min.js',
                  'plugins/jqplot.dateAxisRenderer.min.js',
                  'plugins/jqplot.canvasAxisTickRenderer.min.js']),
        }

    # available plot actions
    ACTIONS = {
        'print': {'label': _('export graph'),
                  'icon': 'icon_png.gif',
                  'js': "cwplot.plotToNewWindow($('#%s'))",
                  },
        'csv': {'label': _('retrieve CSV data'),
                'icon': 'icon_csv.gif',
                'js': 'cwplot.jsonToCsv(cwplot.seriesToArray(cw.cubes.jqplot.plots.%s))',
                },
        }

    def call(self,
             # $.plot arguments
             series_options=None, axes=None, highlighter=None,
             series_defaults=None, axes_defaults=None,
             cursor=False, title=None, legend=None, extra=None,
             # other arguments
             divid=None, width=None, height=None,
             displayfilter=False, mainvar=None,
             displayactions=False, actions=None):
        if self._cw.ie_browser():
            self._cw.add_js('excanvas.js')
        self._cw.add_js(('jquery.jqplot.js', 'cubes.jqplot.js'))
        self._cw.add_css('jquery.jqplot.min.css')
        data, series_options = self.get_series(series_options)
        if series_defaults is None:
            series_defaults = self.default_series_defaults
        if axes_defaults is None:
            axes_defaults = self.default_axes_defaults
        if legend is None:
            legend = self.default_legend
        if axes is None:
            axes = self.default_axes
        if extra is None:
            extra = self.default_extra
        if cursor == True:
            cursor = self.default_cursor
        if cursor:
            self._cw.add_js('plugins/jqplot.cursor.min.js')
        if highlighter or not cursor:
            self._cw.add_js('plugins/jqplot.highlighter.js')
            highlighter_ = self.default_highlighter
            if isinstance(highlighter, dict):
                highlighter_ = highlighter_.copy()
                highlighter_.update(highlighter)
            highlighter = highlighter_
        axes = axes.copy()
        for axis, options in axes.iteritems():
            if 'renderer' in options:
                options = options.copy()
                options['renderer'] = self.renderer(self.axis_renderers,
                                                    options['renderer'])
                axes[axis] = options
            if 'tickRenderer' in options:
                options = options.copy()
                options['tickRenderer'] = self.renderer(self.tick_renderers,
                                                        options['tickRenderer'])
                axes[axis] = options
        if divid is None:
            divid = self._cw.form.get('divid') or u'figure%s' % self._cw.varmaker.next()
        jqplot_args = {
            'seriesDefaults': series_defaults,
            'series': series_options,
            'axesDefaults': axes_defaults,
            'axes': axes,
            'legend': legend,
            'title': title,
            'cursor': cursor,
            'highlighter': highlighter,
            }
        jqplot_args.update(extra)
        self._cw.html_headers.add_onload(self.onload % {
            'id': divid,
            'data': json_dumps(data),
            'jqplotArgs': js_dumps(jqplot_args),
            })
        self.div_holder(divid, width, height)
        if displayfilter and not 'fromformfilter' in self._cw.form:
            self.form_filter(divid, mainvar)
        if displayactions and not 'fromformfilter' in self._cw.form:
            self.display_actions(divid, actions)

    def form_filter(self, divid, mainvar):
        try:
            filterform = self._cw.vreg['views'].select(
                'facet.filtertable', self._cw, rset=self.cw_rset,
                mainvar=mainvar, view=self, **self.cw_extra_kwargs)
        except NoSelectableObject:
            return
        filterform.render(self.w, vid=self.__regid__, divid=divid)

    def display_actions(self, divid, actions=None):
        self._cw.add_css('cubes.jqplot.css')
        self.w(u'<div class="plot-actions">')
        if actions is None:
            actions = self.ACTIONS
        for actionid in actions:
            action = self.ACTIONS[actionid]
            label = self._cw._(action['label'])
            iconurl = self._cw.data_url(action['icon'])
            js = action['js'] % divid
            self.w(u'<a href="javascript: %s" title="%s"><img src="%s" alt="%s"/></a>'
                   % (xml_escape(js), xml_escape(label),
                      xml_escape(iconurl), xml_escape(label)))
        self.w(u'</div><div class="clear"></div>')

    def div_holder(self, divid, width, height):
        style = u''
        if width:
            if isinstance(width, int):
                width = '%spx' % width
            style += 'width: %s;' % width
        if height:
            if isinstance(height, int):
                height = '%spx' % height
            style += 'height: %s;' % height
        self.w(u'<div id="%s" style="%s"></div>' % (divid, style))

    def iter_series(self):
        if self.cw_rset.description[0][0] in ('Date', 'Datetime', 'TZDatetime'):
            abscissa = [datetime2ticks(row[0]) for row in self.cw_rset]
        else:
            abscissa = [row[0] for row in self.cw_rset]
        nbcols = len(self.cw_rset.rows[0])
        for col in xrange(1, nbcols):
            yield filterout_nulls(abscissa, (row[col] for row in self.cw_rset))

    def get_series(self, series_options):
        series = []
        series_options_ = []
        for i, serie in enumerate(self.iter_series()):
            if serie:
                if series_options:
                    options = series_options[i]
                else:
                    options = {}
                if 'renderer' in options:
                    options = options.copy()
                    options['renderer'] = self.renderer(self.renderers,
                                                        options['renderer'])
                series.append(serie)
                series_options_.append(options)
                if 'pointLabels' in options:
                    self._cw.add_js('plugins/jqplot.pointLabels.min.js')
            else:
                self.info('serie %s has no value and will be removed', i)
        return series, series_options_

    def renderer(self, renderers, name):
        jsstr, jsfiles = renderers[name]
        if jsfiles:
            self._cw.add_js(jsfiles)
        return jsstr


class JQPlotView(JQPlotRsetView):
    """same as :class:`JQPlotRsetView` (see there for accepted arguments and
    configuration), but get series from an additional `series` argument that
    should be given at selection, instead of using a result set.
    """
    __regid__ = 'jqplot.default'
    __select__ = match_kwargs('series')

    def iter_series(self):
        return self.cw_extra_kwargs['series']


class JQPlotSimpleView(JQPlotRsetView):

    onload = 'cw.cubes.jqplot.buildPlot("%(id)s", %(data)s, %(options)s);'
    default_legend = {'show': True,
                      'placement': 'e',
                      }
    default_options = {'showDataLabels': True}
    default_renderer = 'bar'

    def call(self, renderer=None, options=None, divid=None, legend=None, colors=None,
             width=450, height=300, displayfilter=False, mainvar=None, title=None,
             displayactions=False, actions=None):
        if self._cw.ie_browser():
            self._cw.add_js('excanvas.js')
        self._cw.add_js('jquery.jqplot.js',)
        self._cw.add_css('jquery.jqplot.min.css')
        data = self.get_data()
        if legend is None:
            legend = self.default_legend
        if divid is None:
            divid = u'figure%s' % self._cw.varmaker.next()
        if renderer is None:
            renderer = self.default_renderer
        serie_options = {'renderer': self.renderer(self.renderers, renderer)}
        if options is None:
            options = self.default_options
        serie_options['rendererOptions']= options
        options = {'series': [serie_options],
                   'legend': legend,
                   'title': title,
                   }
        if colors is not None:
            options['seriesColors'] = colors
        self.set_custom_options(options)
        self._cw.html_headers.add_onload(self.onload % {
            'id': divid,
            'data': json_dumps([data]),
            'options': js_dumps(options)})
        self.div_holder(divid, width, height)
        if displayfilter and not 'fromformfilter' in self._cw.form:
            self.form_filter(divid, mainvar)
        if displayactions and not 'fromformfilter' in self._cw.form:
            self.display_actions(divid, actions)

    def get_data(self):
        # accept a simple list of list as rset.
        return getattr(self.cw_rset, 'rows', self.cw_rset)

    def set_custom_options(self, options):
        pass


class JQPlotPieView(JQPlotSimpleView):
    __regid__ = 'jqplot.pie'
    __select__ = multi_columns_rset(2) # XXX second column are numbers
    default_renderer = 'pie'


class JQPlotDonutView(JQPlotPieView):
    __regid__ = 'jqplot.donut'
    default_renderer = 'donut'


class JQPlotNonPeriodicView(JQPlotSimpleView):
    __regid__ = 'jqplot.nonperiodic'
    __select__ = multi_columns_rset(1)
    default_renderer = 'bar'

    def get_data(self):
        return [float(x[0]) for x in self.cw_rset.rows]


