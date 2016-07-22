(function() {

serieschart = function(domObjId, chart_properties, filename) {
  var width = d3.select(".tab-content").node().getBoundingClientRect().width;
  var height = 600;

  var color = d3.scale.category10();

  d3.csv(filePath+filename, function(error, csv) {
      if (error) throw error;

      color.domain(d3.keys(csv[0]).filter(function(key) { return key !== chart_properties.x_value; }));

      var series = color.domain().map(function(name) {
        return {
          name: name,
          data: csv.map(function(d) {
            return +(+d[name]).toFixed(3);
          })
        };
      });

      var xValues = csv.map(function (d) { return d[chart_properties.x_value]; });

      $("#"+domObjId).highcharts({
          chart: {
            width: width,
            height: height
          },
          title: {
              text: chart_properties['subtitle'],
              x: -20 //center
          },
          xAxis: {
            title: {
              text: chart_properties['x_label']
            },
              categories: xValues
          },
          yAxis: {
              title: {
                  text: chart_properties['y_label']
              },
              plotLines: [{
                  value: 0,
                  width: 1,
                  color: '#808080'
              }]
          },
          tooltip: {
            // pointFormat: '{series.name}: <b>{point.y}</b>',
              // valueSuffix: '%'
          },
          legend: {
              layout: 'vertical',
              align: 'right',
              verticalAlign: 'middle',
              borderWidth: 0
          },
          series: series,
          plotOptions: { series: { marker: { enabled: false } } }
      });
    });
  }
})();
