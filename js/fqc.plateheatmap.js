(function() {
    plateheatmap = function(domObjId, chart_properties, filename) {
        console.log(domObjId);
        var width = d3.select(".tab-content").node().getBoundingClientRect().width;
        var colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"];

        var plateheatmapChart = function(file) {
            d3.csv(file,
            function(d) {
                return {
                    x: d[chart_properties.x_value],
                    y: d[chart_properties.y_value],
                    value: d[chart_properties.value],
                    label: d[chart_properties.label],
                    label_color: d[chart_properties.label_color]
                };
            },
            function(error, data) {
                if (error) throw error;

                var xVals = {};
                data.forEach(function(d){
                    xVals[d.x] = 1;
                });
                xVals = Object.keys(xVals);

                var yVals = {};
                data.forEach(function(d){
                    yVals[d.y] = 1;
                });
                yVals = Object.keys(yVals);

                var labels = {};
                var series = [];
                data.forEach(function(d, i){
                if(d.label)
                    labels[d.label] = 1;
                    series[i] = {"x": xVals.indexOf(d.x),
                                 "y": yVals.indexOf(d.y),
                                 "value": +d.value,
                                 "name": d.label,
                                 "borderColor": d.label_color,
                                 "borderWidth": d.label_color ? 3 : 0,
                                 "pointPadding": d.label_color ? 4 : 3
                    };
                // console.log(series[i]);
                });

                var min = d3.min(data.map(function(d) { return +d.value; }));
                var max = d3.mean(data.map(function(d) { return +d.value; })) * 3;

                labels = Object.keys(labels);
                // console.log(series);
                $(function () {

                    $('#'+domObjId).highcharts({

                        chart: {
                            type: 'heatmap',
                            // marginTop: 40,
                            // marginBottom: 80,
                            plotBorderWidth: 0,
                            width: width,
                            height: 600
                        },

                        plotOptions: {
                            series: {
                                turboThreshold: 0,
                                borderRadius: 25,
                            }
                        },

                        title: {
                            text: chart_properties['subtitle']
                        },

                        xAxis: {
                            categories: xVals,
                            tickLength: 0,
                            lineWidth: 0,
                            minorGridLineWidth: 0,
                            lineColor: "transparent"
                        },

                        yAxis: {
                            categories: yVals,
                            title: {
                                text: null
                            },
                            reversed: true,
                            gridLineColor: "transparent"
                        },

                        colorAxis: {
                            auxarg: true,
                            min: min,
                            max: max,
                            reversed: false,
                            startOnTick: false,
                            endOnTick: false,
                            stops: [[0.125, colors[0]],
                                    [0.250, colors[1]],
                                    [0.375, colors[2]],
                                    [0.500, colors[3]],
                                    [0.625, colors[4]],
                                    [0.750, colors[5]],
                                    [0.875, colors[6]],
                                    [1.000, colors[7]]
                            ],
                        },

                        legend: {
                            align: 'right',
                            layout: 'vertical',
                            margin: 0,
                            verticalAlign: 'top',
                            // verticalAlign: 'middle',
                            y: 25,
                            symbolHeight: 500
                        },

                        tooltip: {
                            formatter:
                                function () {
                                    var label = this.point.name ? '<b>Label:</b> ' + this.point.name : "" ;
                                    return '<b>' + this.series.yAxis.categories[this.point.y] + ':' + this.series.xAxis.categories[this.point.x] + '</b> <br>' +
                                        '<b>Value:</b> ' + this.point.value + '<br>' + label;
                                }
                        },

                        series: [{
                            data: series,
                            dataLabels: {
                                enabled: false
                            }
                        }],

                    });
                });
            });
        };
        plateheatmapChart(filePath+filename);
    }
})();
