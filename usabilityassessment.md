# Usability Assessment

## general
* get rid of phinch header
* fix css
* leaving the filter page for the gallery then returning erases the data that was filtered out ** huge bug **
* add proper breadcrumb functionality / nav
* get rid of sql dependency

## Load data
* get rid of load data page / combine with main data view
* separate biom upload from metadata upload
  * needs to use biom add metadata python function, or rewrite in javascript
  * needs to grab any errors from sys out

## main data view
* make "filter data" look like a header rather than a button
* move "file" info and only keep relevant fields
  * number of otus
  * number of samples
* fix date scrubber snapping
* fix non_numeric_att / empty filter value panel showing partial panel
* add select all / none / inverse to groupable
* get rid of ability to edit phinch name
* add pagination if needed
* move "showing ## samples" to top

## visualization views
* allow user to set metadata column as sample label
* gallery view vis headers are ugly
* remove file size info from these views
* get rid of share, only keep save plot
* fix overlapping search and top seqs floats

### taxonomy bar chart
* add headers to chart options, sort by, etc
  * add ability to sort by metadata
  * put sort category in info box
* raw counts / normalized rather than "value / %"
* get rid of top 10 sequences at bottom
* moving to the right on hover flickers because of popover stealing hover, make this a static infobox rather than dynamic moving

### bubble chart
* get rid of this

### sankey
* typo on click: "Its absolute reads is 3,760,570."

### donut partition
* fix info hover popup
* pick better colors, based on phylogeny
* clicking on wedge should update all bar charts
* one single button to change all from dynamic / standard
* click inside donut to return to overall barchart
* typo "68 Taxonomy in Total"
* donut charts need selected state and bar charts need title

### attributes column chart
* value / normalized
* move dropdown above chart
* add label to dropdown
