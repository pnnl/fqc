(function() {

plateheatmap = function(domObj, chart_properties, filename) {
  var margin = { top: 50, right: 250, bottom: 100, left: 40 },
      width = d3.select(".tab-content").node().getBoundingClientRect().width - margin.left - margin.right,
      // colors = ["#ffffff","#EAEFF9", "#C1D1EF", "#ADC1EA", "#99B2E5", "#84A3E0", "#7093DB", "#4775D1", "#3366CC"];
      colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"];

    function googlec(n) {
      var colores_g = ["#3366cc", "#dc3912", "#ff9900", "#109618", "#990099", "#0099c6", "#dd4477", "#66aa00", "#b82e2e", "#316395", "#994499", "#22aa99", "#aaaa11", "#6633cc", "#e67300", "#8b0707", "#651067", "#329262", "#5574a6", "#3b3eac"];
      return colores_g[n % colores_g.length];
    }

  var plateheatmapChart = function(file) {
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
      // console.log(filename);
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
      data.forEach(function(d){
        if(d.label)
          labels[d.label] = 1;
      });
      labels = Object.keys(labels);

      // var labelColor = d3.scale.category20()
      //   .domain(labels);

      var gridSize = Math.floor(width / xVals.length);
      var buckets = 9;
      var legendElementWidth = Math.floor(width / (buckets + 1));
      var legendElementWidth = width / buckets;
      var height = yVals.length * gridSize;

      var tip = d3.tip()
        .attr('class', 'd3-tip')
        .html(function(d) { return (d.label ? d.label + ": " : "") + d.value; });

      var svg = domObj.append("svg")
          .attr("width", width + margin.left + margin.right)
          .attr("height", height + margin.top + margin.bottom)
          .append("g")
          .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

      svg.call(tip);

      var yLabels = svg.selectAll(".yLabel")
          .data(yVals)
          .enter().append("text")
            .text(function (d) { return d; })
            .attr("x", 0)
            .attr("y", function (d, i) { return i * gridSize; })
            .style("text-anchor", "end")
            .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
            .attr("class", "yLabel mono axis");

      var colorScale = d3.scale.quantile()
          .domain([0, d3.max(data, function (d) { return +d.value; })])
          .range(colors);

      var cards = svg.selectAll(".y")
          .data(data, function(d) {return d.y+':'+d.x;});

      cards.append("title");

      var r = gridSize/2 - 4;

      var xLabels = svg.selectAll(".xLabel")
          .data(xVals)
          .enter().append("text")
            .text(function(d) { return d; })
            .attr("x", function(d, i) { return i * gridSize; })
            .attr("y", 0)
            .style("text-anchor", "left")
            .attr("transform", "translate(" + gridSize / 2 + ", -6)")
            .attr("class", "xLabel mono axis")

      cards.enter().append("circle")
          .attr("class", function(d) { return "y bordered " + d.class; })
          .attr("cx", function(d, i) { return (xVals.indexOf(d.x)) * gridSize + r + 10; })
          .attr("cy", function(d, i) { return (yVals.indexOf(d.y)) * gridSize + r + 10; })
          .attr("r", r)
          .attr("width", gridSize)
          .attr("height", gridSize)
          .style("fill", colors[0])
          .style("stroke", function(d) { return d.label ? googlec(labels.indexOf(d.label)) : "#f3f3f3"; })
          .style("stroke-width", function(d) { return d.label ? 5 : 2; })
          .on('mouseover', tip.show)
          .on('mouseout', tip.hide);

      cards.transition().duration(1000)
          .style("fill", function(d) { return colorScale(d.value); });

      cards.select("title").text(function(d) { return d.value; });

      cards.exit().remove();

      var legend = svg.selectAll(".legend")
          .data([0].concat(colorScale.quantiles()), function(d) { return d; });

      legend.enter().append("g")
          .attr("class", "legend");

      legend.append("rect")
        .attr("x", function(d, i) { return legendElementWidth * i; })
        .attr("y", height + 10)
        .attr("width", legendElementWidth)
        .attr("height", gridSize / 2)
        .style("fill", function(d, i) { return colors[i]; });

      legend.append("text")
        .attr("class", "mono")
        .text(function(d) { return "≥ " + Math.round(d); })
        .attr("x", function(d, i) { return legendElementWidth * i; })
        .attr("y", height + gridSize);

      legend.exit().remove();

    var borderPath = svg.append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("height", height + 10)
        .attr("width", width)
        .style("stroke", '#C0C0C0')
        .style("fill", "none")
        .style("stroke-width", 1);

    });
  };

  plateheatmapChart(filePath+filename);
}

})();
