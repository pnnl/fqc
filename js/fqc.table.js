(function() {

table = function(domObj, chart_properties, filename) {
  d3.text(filePath+filename, function(error, data) {
		if (error) throw error;

		var parsedCSV = d3.csv.parseRows(data);
		var header = parsedCSV.shift();
		var table = domObj.append("table")
			.attr("class", "table table-hover");

		table.append("thead").append("tr").selectAll("th")
				.data(header).enter()
				.append("th")
				.text(function(d) { return d; });

		table.append("tbody").selectAll("tr")
          .data(parsedCSV).enter()
          .append("tr")

      .selectAll("td")
          .data(function(d) { return d; }).enter()
          .append("td")
          .text(function(d) { return d; });

    $('.table').DataTable();
	});
}
})();
