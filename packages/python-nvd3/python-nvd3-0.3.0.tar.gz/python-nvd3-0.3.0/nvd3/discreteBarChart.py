#!/usr/bin/python
# -*- coding: utf-8 -*-
from NVD3Chart import NVD3Chart


class discreteBarChart(NVD3Chart):
    """
    A discrete bar chart or bar graph is a chart with rectangular bars with
    lengths proportional to the values that they represent.

    .. image:: ../_static/screenshot/discreteBarChart.png

    Python example::

        from nvd3 import discreteBarChart
        chart = discreteBarChart(name='discreteBarChart', height=400, width=400)

        xdata = ["A", "B", "C", "D", "E"]
        ydata = [3, 4, 0, -3, 5, 7]

        extra_serie = {"tooltip": {"y_start": "", "y_end": " balls"}}
        chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
        chart.buildhtml()

    Javascript generated::

        data = [{ key: "Cumulative Return",
                  values: [
                    {
                      "label": "A",
                      "value" : 10
                    },
                    {
                      "label": "B",
                      "value" : 0
                    },
                    {
                      "label": "C",
                      "value" : -3
                    },
                  ]
                }]

        nv.addGraph(function() {
            var chart = nv.models.discreteBarChart()
                .x(function(d) { return d.label })
                .y(function(d) { return d.value })
                .showLabels(true);
            chart.tooltipContent(function(key, y, e, graph) {
                var x = String(graph.point.x);
                var y = String(graph.point.y);
                if(key == 'Serie 1'){
                    var y =  String(graph.point.y)  + ' balls';
                }
                tooltip_str = '<center><b>'+key+'</b></center>' + y + ' at ' + x;
                return tooltip_str;
            });
            d3.select("#div_id")
                .datum(data)
                .transition()
                .duration(1200)
                .call(chart);

            return chart;
        });
    """
    def __init__(self, height=450, width=None, **kwargs):
        NVD3Chart.__init__(self, **kwargs)
        self.create_x_axis('xAxis', format=None)
        self.create_y_axis('yAxis', format=None)
        # must have a specified height, otherwise it superimposes both chars
        if height:
            self.set_graph_height(height)
        if width:
            self.set_graph_width(width)
