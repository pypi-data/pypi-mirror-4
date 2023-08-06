// process CSV file with read quality binning
// - based on the tutorial on the d3.js site - LG

//var basequal_max = 64;
var basepos_max = 75;
var w = Math.floor(screen.width * .75),
    bw = w / basepos_max,
    h = 150,
    p = 25;

var x = d3.scale.linear()
    .domain([0, basepos_max])
    .range([p, w+p]);

var y = d3.scale.linear()
    .domain([0, basequal_max])
    .range([h, 0]);


function qualityplot(data, i) {
    
    // Convert strings to numbers.
    data.forEach(function(d) {
	d.basepos = +d.basepos;
    	d.p10 = +d.p10;
    	d.p25 = +d.p25;
    	d.p50 = +d.p50;
    	d.p75 = +d.p75;
    	d.p90 = +d.p90;
    });

    //console.debug(data);

    var barplot = d3.select("#qualityplot_" + i)
	.append("svg")
	.attr("class", "chart")
	.attr("width", "100%" )
	.attr("height", h + p )
        .attr("viewBox", "0 0 "+(w+p)+" "+(h+p));
        //.attr("preserveAspectRatio", "xMidyMid");

    // x-axis
    barplot.selectAll("g.x.axis")
	.data(x.ticks(10))
	.enter().append("line")
	.attr("x1", x)
	.attr("x2", x)
	.attr("y1", 0)
	.attr("y2", h)
	.style("stroke", "#ccc");

    barplot.selectAll("x.rule")
	.data(x.ticks(10))
	.enter().append("text")
	.attr("class", "rule")
	.attr("x", x)
	.attr("y", h + p)
	.attr("text-anchor", "middle")
	.text(String);

    // y-axis
    barplot.selectAll("g.y.axis")
	.data(y.ticks(5))
	.enter().append("line")
	.attr("x1", p)
	.attr("x2", w+p)
	.attr("y1", y)
	.attr("y2", y)
	.style("stroke", "#ccc");

    barplot.selectAll("y.rule")
	.data(y.ticks(5))
	.enter().append("text")
	.attr("class", "rule")
	.attr("x", "2em")
	.attr("y", y)
	.attr("dx", "0em")
	.attr("dy", ".5em")
	.attr("text-anchor", "end")
	.text(String);

    // boxes
    barplot.selectAll("line.p90")
	.data(data)
	.enter().append("line")
	.attr("class", "p90")
	.attr("x1", function(d) { return x(d.basepos) + p + bw / 2- 0.5; })
	.attr("x2", function(d) { return x(d.basepos) + p + bw / 2 - 0.5; })
	.attr("y1", function(d) { return y(d.p10) - 0.5; })
	.attr("y2", function(d) { return y(d.p90) - 0.5; });
    barplot.selectAll("rect")
    	.data(data)
    	.enter().append("rect")
    	.attr("x", function(d) { return x(d.basepos) + p - 0.5; })
	.attr("y", function(d) { return y(d.p75) - 0.5; })
	.attr("width", bw)
	.attr("height", function(d) { return h-y(d.p75-d.p25); })
    barplot.selectAll("line.center")
	.data(data)
	.enter().append("line")
	.attr("x1", function(d) { return x(d.basepos) + p - 0.5; })
	.attr("x2", function(d) { return x(d.basepos) + p + bw - 0.5; })
	.attr("y1", function(d) { return y(d.p50) - 0.5; })
	.attr("y2", function(d) { return y(d.p50) - 0.5; })
	.style("stroke", "#fff");

    barplot.append("line")
	.attr("x1", 0 + p)
	.attr("x2", 0 + p)
	.attr("y1", 0 - 0.5)
	.attr("y2", h - 0.5)
	.style("stroke", "#000");

    barplot.append("line")
	.attr("x1", p)
	.attr("x2", w+p)
	.attr("y1", 0)
	.attr("y2", 0)
	.style("stroke", "#000");

    barplot.append("line")
	.attr("x1", p)
	.attr("x2", w+p)
	.attr("y1", h)
	.attr("y2", h)
	.style("stroke", "#000");

    barplot.append("line")
	.attr("x1", w + p)
	.attr("x2", w + p)
	.attr("y1", 0 - 0.5)
	.attr("y2", h - 0.5)
	.style("stroke", "#000");

}

