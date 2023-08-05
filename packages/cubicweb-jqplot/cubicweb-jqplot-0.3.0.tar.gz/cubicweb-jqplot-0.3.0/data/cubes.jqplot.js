cw.cubes.jqplot = new Namespace('cw.cubes.jqplot');
$.extend(cw.cubes.jqplot, {
    // a place to register created plots.
    plots: {},

    buildPlot: function(divid, data, options) {
      cw.cubes.jqplot.plots[divid] = $.jqplot(divid, data, options);
    }

});
