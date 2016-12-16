
(function() {

arearange = function(domObjId, chart_properties, filename) {
  var labels = false; // show the text labels beside individual boxplots?
  var width = d3.select(".tab-content").node().getBoundingClientRect().width;
  var height = 600;

  d3.csv(filePath+filename, function(error, csv) {
    if (error) throw error;

    var data = [];
    var ranges = [];
    var averages = [];
    var zones = [];

    csv.forEach(function(x, i) {
      // console.log(x);
      data[i] = x;
      ranges[i] = [x[chart_properties.x_value], +(+x[chart_properties.lower_quartile]).toFixed(3),
      +(+x[chart_properties.upper_quartile]).toFixed(3)];
      if(chart_properties.mean)
        averages[i] = [x[chart_properties.x_value], +(+x[chart_properties.mean]).toFixed(3)]
    });

    $('#'+domObjId).highcharts({
        chart: {
          width: width,
          height: height
        },
        title: {
            text: chart_properties['subtitle']
        },
        xAxis: {
            type: 'category',
            title: {
              text: chart_properties['x_label']
            }
        },

        yAxis: {
            title: {
                text: chart_properties['y_label']
            }
        },

        tooltip: {
            crosshairs: true,
            shared: true
            // valueSuffix: '°C'
        },

        legend: {
        },

        series: [{
            name: "Mean",
            data: averages,
            zIndex: 1,
            marker: {
                enabled: false
            },
            zones: chart_properties.zones
        }, {
            name: "Inter-Quartile Range",
            data: ranges,
            type: 'arearange',
            lineWidth: 0,
            linkedTo: ':previous',
            color: Highcharts.getOptions().colors[0],
            fillOpacity: 0.3,
            zIndex: 0,
            zones: chart_properties.zones
        }]
    });
  });
}

})();
