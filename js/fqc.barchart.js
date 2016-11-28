(function() {

barchart = function(domObjId, chart_properties, filename) {
  var width = d3.select(".tab-content").node().getBoundingClientRect().width;
  var height = 600;
  var color = d3.scale.category10();

  /**
   * Get histogram data out of xy data
   * @param   {Array} data  Array of tuples [x, y]
   * @param   {Number} step Resolution for the histogram
   * @returns {Array}       Histogram data
   */
  function histogram(data, step) {
      var histo = {},
          x,
          i,
          arr = [];

      // Group down
      for (i = 0; i < data.length; i++) {
          x = Math.floor(data[i][0] / step) * step;
          if (!histo[x]) {
              histo[x] = 0;
          }
          histo[x]++;
      }

      // Make the histo group into an array
      for (x in histo) {
          if (histo.hasOwnProperty((x))) {
              arr.push([parseFloat(x), histo[x]]);
          }
      }

      // Finally, sort the array
      arr.sort(function (a, b) {
          return a[0] - b[0];
      });

      return arr;
  }

  d3.csv(filePath+filename, function(error, csv) {
      if (error) throw error;

      var xValues = csv.map(function (d) { return d[chart_properties.x_value]; });

      var data = csv.map(function(d) {
        return [+d[chart_properties.x_value], +d[chart_properties.y_value]];
      });

      $("#"+domObjId).highcharts({
          chart: {
            type: 'column',
            width: width,
            height: height
          },
          title: {
              text: chart_properties['subtitle'],
              x: -20 //center
          },
          xAxis: {
            // gridLineWidth: 1
            categories: xValues,
            title: {
                text: null
            }
          },
          yAxis: {
              title: {
                  text: chart_properties.y_label
              }
          },
          tooltip: {
              formatter: function() {
                  return chart_properties.x_label + ": <b>" + this.x + '</b><br>' + chart_properties.y_label + ": <b>" + this.y + "</b>";
              }
          },
          legend: {
              enabled: false
          },
          series: [{
            name: chart_properties['subtitle'],
            data: data
          }]
      });
    });
  }
})();
