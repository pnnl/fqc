(function() {

heatmap = function(domObjId, chart_properties, filename) {
  var width = d3.select(".tab-content").node().getBoundingClientRect().width;
      //colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"];

  var heatmapChart = function(file) {
    d3.csv(file,
    function(d) {
      // console.log(d);
      return {
        x: d[chart_properties.x_value],
        y: d[chart_properties.y_value],
        value: d[chart_properties.value],
        label: d[chart_properties.label]
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
        series[i] = [xVals.indexOf(d.x), yVals.indexOf(d.y), +d.value];
        // console.log(series[i]);
      });

      var min = d3.min(data.map(function(d) { return +d.value; }));

      labels = Object.keys(labels);
      // console.log(series);
      $(function () {

          $('#'+domObjId).highcharts({

              chart: {
                  type: 'heatmap',
                  // marginTop: 40,
                  // marginBottom: 80,
                  plotBorderWidth: 1,
                  width: width,
                  height: 600
              },

              plotOptions: {
                      series: {
                          turboThreshold:0
                      }
              },

              title: {
                  text: chart_properties['subtitle']
              },

              xAxis: {
                  categories: xVals
              },

              yAxis: {
                  categories: yVals,
                  title: {
                    text: chart_properties['y_label']
                  }
              },

              colorAxis: {
                  min: chart_properties['min'],
                  max: chart_properties['max'],
                  reversed: false,
                  stops: [
                      [0, ((chart_properties['min_color']) ? chart_properties['min_color'] : "#36c")],
                      [0.5, ((chart_properties['mid_color']) ? chart_properties['mid_color'] : "#ffffff")],
                      [0.9, ((chart_properties['max_color']) ? chart_properties['max_color'] : "#dc3912")]
                  ],
              },

              legend: {
                  align: 'right',
                  layout: 'vertical',
                  margin: 0,
                  verticalAlign: 'top',
                  y: 25,
                  symbolHeight: 500
              },

              tooltip: {
                  formatter: function () {
                      return '<b>' + this.series.xAxis.categories[this.point.x] + ' @ '+ this.series.yAxis.categories[this.point.y] + '</b> <br>' +
                          this.point.value;
                  }
              },

              series: [{
                  borderWidth: ((chart_properties['border_width']) ? chart_properties['border_width'] : 0),
                  data: series
              }],

          });
      });

    });
  };
  heatmapChart(filePath+filename);
}

})();
