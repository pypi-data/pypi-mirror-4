
function buildFloatTickFormatter(precision) {
    function floatTickFormatter(format, val) {
        var power = Math.pow(10, precision || 0);
        return String(Math.round(val * power) / power);
    }
    return floatTickFormatter
}

floatTickFormatter = buildFloatTickFormatter(1);

function hoursTickFormatter(format, val) {
    hours = Math.floor(val)
    minutes = Math.round((val - hours) * 60)
    if (minutes == 60) {
        hours += 1;
        minutes = 0;
    }
    if (hours < 0)
        hours = '-' + (-(hours + 1))
    if (minutes != 0) {
        return String(hours + 'h' + minutes + 'm')
    }
    return String(hours + 'h')
}


function dateTickFormatter(format, val) {
    return $.jsDate.strftime(val, format);
};


function monthTickFormatter(format, val) {
    if (val < 100) { return ''; } // XXX coordinate box sent erroneous value
    year = Math.floor(val / 12);
    month = (val % 12) + 1;
    return year + '/' + month;
}


cwplot = new Namespace('cwplot');

/* PNG export *****************************************************************/

jQuery.extend(cwplot, {
    /**
     * .. function:: cwplot.plotToNewWindow($plot)
     *
     * draw data from the given plot (including title, legend & all) in a canvas
     * and open it as PNG is a new window
     */
    plotToNewWindow: function($plot) {
        var img = $plot.jqplotToImage();
        if (img) {
            open(img.toDataURL("image/png"));
        }
    }
});

// code below is coming from
// https://bitbucket.org/cleonello/jqplot/issue/14/export-capabilities#comment-554274
// changes by Logilab:
// * check border width before drawing it
// * don't attempt to auto wrap text, search for <br> instead
$(function() {
    $.fn.jqplotToImage = function() {
        var obj = $(this);
        var newCanvas = document.createElement("canvas");
        var size = cwplot.findPlotSize(obj);
        newCanvas.width = size.width;
        newCanvas.height = size.height;
        // check for plot error
        var baseOffset = obj.offset();
        if (obj.find("canvas.jqplot-base-canvas").length) {
            baseOffset = obj.find("canvas.jqplot-base-canvas").offset();
            baseOffset.left -= parseInt(obj.css('margin-left').replace('px', ''));
        }
        // fix background color for pasting
        var context = newCanvas.getContext("2d");
        var backgroundColor = "rgba(255,255,255,1)";
        obj.children(':first-child').parents().each(function () {
            if ($(this).css('background-color') != 'transparent') {
                backgroundColor = $(this).css('background-color');
                return false;
            }
        });
        context.fillStyle = backgroundColor;
        context.fillRect(0, 0, newCanvas.width, newCanvas.height);
        // add main plot area
        obj.find('canvas').each(function () {
            var offset = $(this).offset();
            newCanvas.getContext("2d").drawImage(this,
                offset.left - baseOffset.left,
                offset.top - baseOffset.top
            );
        });
        obj.find(".jqplot-series-canvas > div").each(function() {
            var offset = $(this).offset();
            var context = newCanvas.getContext("2d");
            context.fillStyle = $(this).css('background-color');
            var paddingLeft = parseInt($(this).css('padding-left').replace('px', ''));
            var paddingRight = parseInt($(this).css('padding-right').replace('px', ''));
            var paddingTop = parseInt($(this).css('padding-top').replace('px', ''));
            var paddingBottom = parseInt($(this).css('padding-bottom').replace('px', ''));
            context.fillRect(
                offset.left - baseOffset.left - paddingLeft,
                offset.top - baseOffset.top,
                $(this).width() + paddingLeft + paddingRight,
                $(this).height() + paddingTop + paddingBottom
            );
            cwplot.copyText(context, $(this), offset.left - baseOffset.left, offset.top - baseOffset.top - paddingTop, $(this).width());
        });
        // add x-axis labels, y-axis labels, point labels
        obj.find('div.jqplot-axis > div, div.jqplot-point-label, div.jqplot-error-message, .jqplot-data-label, div.jqplot-meterGauge-tick, div.jqplot-meterGauge-label').each(function() {
            var offset = $(this).offset();
            var context = newCanvas.getContext("2d");
            cwplot.copyText(context, $(this), offset.left - baseOffset.left, offset.top - baseOffset.top - 2.5, $(this).width());
        });
        // add the title
        obj.children("div.jqplot-title").each(function() {
            var offset = $(this).offset();
            var context = newCanvas.getContext("2d");
            cwplot.copyText(context, $(this), offset.left - baseOffset.left, offset.top - baseOffset.top,
                            newCanvas.width - parseInt(obj.css('margin-left').replace('px', '')) - parseInt(obj.css('margin-right').replace('px', '')));
        });
        // add the legend
        obj.children("table.jqplot-table-legend").each(function() {
            var offset = $(this).offset();
            var context = newCanvas.getContext("2d");
            if ($(this).css('border-top-width') != '0px') {
                context.strokeStyle = $(this).css('border-top-color');
                context.strokeRect(
                    offset.left - baseOffset.left,
                    offset.top - baseOffset.top,
                    $(this).width(), $(this).height()
                );
            }
            context.fillStyle = $(this).css('background-color');
            context.fillRect(
                offset.left - baseOffset.left,
                offset.top - baseOffset.top,
                $(this).width(), $(this).height()
            );
        });
        // add the swatches
        obj.find("div.jqplot-table-legend-swatch").each(function() {
            var offset = $(this).offset();
            var context = newCanvas.getContext("2d");
            if ($(this).css('border-top-width') != '0px') {
                context.fillStyle = $(this).css('border-top-color');
                context.fillRect(
                    offset.left - baseOffset.left,
                    offset.top - baseOffset.top,
                    $(this).parent().width(),$(this).parent().height()
                );
            }
        });
        obj.find("td.jqplot-table-legend").each(function() {
            var offset = $(this).offset();
            var context = newCanvas.getContext("2d");
            context.textBaseline = $(this).css('vertical-align');
            cwplot.copyText(context, $(this), offset.left-baseOffset.left, offset.top - baseOffset.top + parseInt($(this).css('padding-top').replace('px','')), $(this).width());
        });
        return newCanvas;
    };
});


jQuery.extend(cwplot, {

    getLineheight: function(obj) {
        var lineheight;
        if (obj.css('line-height') == 'normal') {
            lineheight = obj.css('font-size');
        } else {
            lineheight = obj.css('line-height');
        }
        return parseInt(lineheight.replace('px',''));
    },

    getTextAlign: function(obj) {
        var textalign = obj.css('text-align');
        if (textalign == '-webkit-auto') {
            textalign = 'left';
        }
        return textalign;
    },

    copyText: function(context, $this, x, y, fitWidth) {
        if (!$.trim($this.text())) {
            return; // no text to copy
        }
        // initialize context
        context.font = [$this.css('font-style'), $this.css('font-size'), $this.css('font-family')].join(' ');
        context.fillStyle = $this.css('color');
        context.textAlign = cwplot.getTextAlign($this);
        var lineheight = cwplot.getLineheight($this);
        if (context.textAlign == 'center') {
            x += fitWidth/2;
        }
        if (context.textBaseline == 'middle') {
            y -= lineheight/2;
        } else if(context.textBaseline == 'top') {
            y -= lineheight;
        }
        var textArr = $.trim($this.html()).split(/<br[^>]*>/g);
        for (idx = textArr.length - 1; idx >= 0; idx--) {
            var line = textArr.pop().replace(/<[^>]*>/g, '');
            if (context.measureText(line).width > fitWidth && context.textAlign == 'center') {
                x -= fitWidth/2;
                context.textAlign = 'left';
                context.fillText(line, x, y + (idx+1) * lineheight);
                context.textAlign = 'center';
                x += fitWidth/2;
            } else {
                context.fillText(line, x, y + (idx+1) * lineheight);
            }
        }
    },

    findPlotSize: function(obj) {
        var width = obj.width();
        var height = obj.height();
        var legend = obj.find('.jqplot-table-legend');
        if (legend.position()) {
            height = legend.position().top + legend.height();
        }
        var objOffset = obj.offset();
        obj.find('*').each(function() {
            var offset = $(this).offset();
            tempWidth = offset.left + $(this).width() -  objOffset.left;
            tempHeight = $(this).height();
            if(tempWidth > width) {
                width = tempWidth;
            }
            if(tempHeight > height) {
                height = tempHeight;
            }
        });
        return {width: width, height: height};
    }
});


/* CSV export *****************************************************************/

jQuery.extend(cwplot, {
    /**
     * .. function:: function cwplot.seriesToArray(jqplot)
     *
     * turn jqplot's series into a 2D javascript array suitable  for CSV export
     */
    seriesToArray: function(jqplot) {
        var array = [];
        // index in each serie
        var idxArray = [];
        var headers = ['abscisse']
        for (var i = 0; i < jqplot.series.length; i++) {
            idxArray.push(0);
            headers.push(jqplot.series[i].label);
        }
        array.push(headers);
        while (true) {
            // current abscissa
            var cabscissa = null;
            // compute minimal abscissa
            for (var i = 0; i < jqplot.series.length; i++) {
                var serie = jqplot.series[i].data;
                var idx = idxArray[i];
                if (idx == serie.length){
                    continue
                } else if (cabscissa == null || serie[idx][0] < cabscissa) {
                    cabscissa = serie[idx][0];
                }
            }
            if (cabscissa == null) break;
            var row = [];
            row.push(cabscissa);
            // write current row
            for (var i = 0; i < jqplot.series.length; i++) {
                var serie = jqplot.series[i].data;
                var idx = idxArray[i];
                if (idx == serie.length) {
                    row.push(null);
                } else if (serie[idx][0] == cabscissa) {
                    row.push(serie[idx][1]);
                    idxArray[i] += 1
                } else {
                    row.push(null);
                }
            }
            array.push(row);
        }
        return array;
    },

    /**
     * .. function:: function cwplot.jsonToCsv(array)
     *
     * turn a javascript 2D array into downloadable CSV data
     */
    jsonToCsv: function(array) {
        var str = '';
        for (var i = 0; i < array.length; i++) {
            var line = '';
            for (var j = 0; j < array[i].length; j++) {
                var val = array[i][j];
                if (val != null) {
                    if (typeof(val) == "string") {
                        // proprify string: remove <br/> and <a> links
                        val = val.replace('<br/>', ' ');
                        var match = /<a[^>]*>(.*)<\/a>/.exec(val);
                        if (match != null) {
                            val = match[1];
                        }
                        // XXX quote
                    }
                    line += val;
                }
                line += '\t';
            }
            str += line + '\r\n';
        }
        if (navigator.appName != 'Microsoft Internet Explorer') {
            window.open('data:text/csv;filename=export.csv;charset=utf-8,' + escape(str));
        } else {
            var popup = window.open('', 'csv', '');
            popup.document.body.innerHTML = '<pre>' + str + '</pre>';
        }
    }
});
