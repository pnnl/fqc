(function() {

boxplot = function(domObj, chart_properties, filename) {
  var labels = false; // show the text labels beside individual boxplots?
  var margin = {top: 30, right: 0, bottom: 90, left: 50};
  var width = d3.select(".tab-content").node().getBoundingClientRect().width - margin.left - margin.right;
  var height = 400 - margin.top - margin.bottom;

  var min = 0,
      max = 40;

  d3.csv(filePath+filename, function(error, csv) {
    if (error) throw error;

    var data = [];

    csv.forEach(function(x, i) {
      data[i] = x;
          i = i + 1
    });

    var chart = d3.box()
      .height(height)
      .domain([min, max])
      .showLabels(labels)
      .median(chart_properties.median)
      .upper_quartile(chart_properties.upper_quartile)
      .lower_quartile(chart_properties.lower_quartile)
      .upper_percentile(chart_properties.upper_percentile)
      .lower_percentile(chart_properties.lower_percentile);

    var svg = domObj.append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .attr("class", "box")
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // the x-axis
    var x = d3.scale.ordinal()
      .domain( data.map(function(d) { return d.Base } ) )
      .rangeRoundBands([0, width], 0.5, 0.2);
    var xAxis = d3.svg.axis()
      .scale(x)
          .tickFormat(function(d) {return d.split("-")[0];})
          .orient("bottom");
    // the y-axis
    var y = d3.scale.linear()
      .domain([min, max])
      .range([height + margin.top, 0 + margin.top]);

    var yAxis = d3.svg.axis()
          .scale(y)
          .orient("left");
    // draw the boxplots
    svg.selectAll(".box")
        .data(data)
      .enter().append("g")
      .attr("transform", function(d) { return "translate(" + x(d.Base) + "," + margin.top + ")"; } )
        .call(chart.width(x.rangeBand()));

     // draw y axis
    svg.append("g")
          .attr("class", "y axis")
          .call(yAxis)
      .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0 - margin.left)
        .attr("x", 0 - (height / 2) - margin.top)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .style("font-size", "16px")
        .text("Quality Score");

    // draw x axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + (height + margin.top) + ")")
        .call(xAxis)
        .selectAll("text")
          .attr("y", 15)
          .attr("x", -15)
          .attr("dy", ".25em")
          .attr("transform", "rotate(-45)")
          .attr("text-anchor", "start");

    if(chart_properties.mean)
    {
      var line = d3.svg.line()
        .x(function(d) { return x(d.Base) + x.rangeBand()*.5; })
        .y(function(d) { return y(d[chart_properties.mean]); });

      svg.append("path")
        .datum(data)
        .attr("class", "redline")
        .attr("d", line);
    }
  });
}

})();
