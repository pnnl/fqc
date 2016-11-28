var filePath = "/fqc/tests/data/qc/plot_data/"
var groupsDict = {};
var groupOptions;
var uidSelect;
var uidOptions;
var groupSelect;
var groupOptions;
var currUid;

// $("#panel_body").height($( document ).height() - $("#panel_body").offset().top);

queue()
	.defer(d3.json, filePath+"groups.json")
	.await(makeGroupSelect);

function makeGroupSelect(error, groups) {
	if (error) throw error;

	groups.forEach(function(d){
		groupsDict[d.group_id] = d.uids;
	});

	groupSelect  = d3.select("#groupSelector")
    .append("select")
    .attr("class", "form-control")
    .on("change", function(){
      currGroup = getCurrentGroup();
      updateUidSelect(currGroup);
  });

  groupOptions = groupSelect.selectAll("option").data(groups);
  groupOptions.enter()
    .append("option")
    .text(function(d) { return d.group_id; });

	currGroup = groups[0].group_id;

	makeUidSelect(groupsDict[currGroup]);
}

function getCurrentGroup() {
	var selectedIndex = groupSelect.property("selectedIndex"),
			currGroup = groupOptions[0][selectedIndex].__data__;
	return currGroup;
}

function makeUidSelect(uids) {
  uidSelect  = d3.select("#uidSelector")
    .append("select")
    .attr("class", "form-control")
    .on("change", function(){
      var selectedIndex = uidSelect.property("selectedIndex"),
          currUid = uidOptions[0][selectedIndex].__data__;
        loadUidData(currUid);
  });

  uidOptions = uidSelect.selectAll("option").data(uids);

  uidOptions.enter()
    .append("option");

	uidOptions
    .text(function(d) { return d; });

	uidOptions.exit().remove();

	currUid = uids[0];
	loadUidData(currUid);
}

function updateUidSelect(group) {
	var uids = group.uids;
	uidOptions = uidSelect.selectAll("option").data(uids);

	uidOptions.enter()
		.append("option");

	uidOptions
		.text(function(d) { return d; });

	uidOptions.exit().remove();

	currUid = uids[0];
	loadUidData(currUid);
}

function loadUidData(uid) {
  console.log("Loading data for uid "+uid);
	currUid = uid;
	var currGroup = getCurrentGroup();

  queue()
  	.defer(d3.json, filePath + currGroup.group_id + "/" + uid + "/config.json")
  	.await(populateTabs);
}

function populateTabs(error, data) {
  if (error) throw error;

	data.forEach(function(d){
		d.tab_id = d.tab_name.replace(/\W/g, '');
	});

	var currGroup = getCurrentGroup();
  var uidDataFolder = currGroup.group_id+"/"+currUid;

	//need to preload all the data...
	d3.select("#metricsNav").selectAll("li").remove();
  var tabs = d3.select("#metricsNav")
		.selectAll("li")
		.data(data, function(d){
			return currUid+d.tab_id;
		});

  tabs.enter().append("li");

  tabs
		.attr("role", "presentation")
    .append("a")
    .attr("href", function(d) { return "#"+d.tab_id; })
    .append("small")
    .text(function(d) { return d.tab_name; })
    .append("span")
    .attr("class", function(d){
      var c = "status-icon glyphicon ";
      return c + (d.status == "pass" ? "green glyphicon-ok-sign" : d.status == "fail" ? "red glyphicon-remove-sign" : d.status == "warn" ? "yellow glyphicon-question-sign" : "");
    })
    .attr("aria-hidden", "true");

	d3.select("#tabContent").selectAll("div").remove();
  var tabContent = d3.select("#tabContent").selectAll("div")
		.data(data, function(d) { return currUid+d.tab_id+"tabContent"; });

  tabContent.enter().append("div");

	tabContent
    .attr("role", "tabpanel")
    .attr("class", "tab-pane")
    .attr("id", function(d){
      return d.tab_id;
    });

	tabContent.exit().remove();

	data.forEach(function(d){
		if(d.filename instanceof Object)
		{
			var nestedTabGroup = d3.select("#"+d.tab_id)
				.append("ul")
				.attr("id", d.tab_id+"_tabGroup")
				.attr("class", "nav nav-tabs")
				.attr("role", "tablist")
				.selectAll("li").data(d.filename);

			d.filename.forEach(function(p){
				p.id = p[0].replace(/\W/g, '');
			});

			nestedTabGroup.enter()
				.append("li");

			nestedTabGroup
				.attr("role", "presentation")
				.append("a")
					.attr("aria-controls", function(p) { return p.id; })
					.attr("href", function(p) { return "#"+d.tab_id+"_"+p.id; })
					.attr("role", "tab")
					.attr("data-toggle", "tab")
					.text(function(p) { return p[0]; });

			nestedTabGroup.exit().remove();

			var nestedTabContent = d3.select("#"+d.tab_id).append("div")
				.attr("class", "tab-content")
				.selectAll("div").data(d.filename);

			nestedTabContent.enter()
				.append("div");

			nestedTabContent
				.attr("role", "tabpanel")
				.attr("class", "tab-pane")
				.attr("id", function(p) { return d.tab_id+"_"+p.id; });

			nestedTabContent.exit().remove();

			d.filename.forEach(function(p){
				 makeChart(d.tab_id+"_"+p.id,d.chart_properties, uidDataFolder+"/"+p[1]);
			});

			$("#"+d.tab_id+"_tabGroup a").click(function (e) {
				e.preventDefault()
				$(this).tab("show")
			});

			$("#"+d.tab_id+"_tabGroup a:first").tab("show");
		} else {
			makeChart(d.tab_id,d.chart_properties,uidDataFolder+"/"+d.filename)
		}
	});

	tabs.exit().remove();

  $("#metricsNav a").click(function (e) {
    e.preventDefault()
    $(this).tab("show")
  });

	$("#metricsNav a:first").tab("show");
}

function makeChart(domObjId, chart_properties, filename) {
	var domObj = d3.select("#"+domObjId);

	if(chart_properties.type == "table")
		table(domObj, chart_properties, filename);
	else if(chart_properties.type == "line")
		serieschart(domObjId, chart_properties, filename);
	else if(chart_properties.type == "arearange")
		arearange(domObjId, chart_properties, filename);
	else if(chart_properties.type == "heatmap")
		heatmap(domObjId, chart_properties, filename)
	else if(chart_properties.type == "plateheatmap")
		plateheatmap(domObj, chart_properties, filename)
	else if(chart_properties.type == "histogram")
		histogramchart(domObjId, chart_properties, filename)
	else if(chart_properties.type == "bar")
		barchart(domObjId, chart_properties, filename)
	else {
		domObj.append("div")
			.attr("class", "alert alert-danger")
			.attr("role", "alert")
			.html("Sorry, <strong>" + chart_properties.type + "</strong> is not a supported chart type.")
	}
}
