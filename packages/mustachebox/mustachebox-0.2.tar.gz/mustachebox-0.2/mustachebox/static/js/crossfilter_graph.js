// globals given by either d3.js or crossfilter
var d3, nestByDate, crossfilter, barChart, window;
// the data
var  record, recordEnter, chart, charts, list;
// the dimensions used in this file
var all, date, dates, hour, hours, ram, rams, cpu, cpus, la1, la1s;
// Various formatters.
var formatNumber = d3.format(",d"),
    formatChange = d3.format("+,d"),
    formatDate = d3.time.format("%B %d, %Y"),
    formatTime = d3.time.format("%I:%M %p");
// chart var
var gBrush, extent;
var url;
"use strict";

// Like d3.time.format, but faster.
function parseDate(d) {
    return new Date(d * 1000);
}


function recordList(div) {
    var recordsByDate = nestByDate.entries(date.top(40));
    div.each(function () {
        var date = d3.select(this).selectAll(".date")
            .data(recordsByDate, function (d) { return d.key; });
        date.enter().append("div")
            .attr("class", "date")
            .append("div")
            .attr("class", "day")
            .text(function (d) { return d.instance; });
        date.exit().remove();
        record = date.order().selectAll(".record")
            .data(function (d) {return d.values; }, function (d) { return d.index; });
        recordEnter = record.enter().append("div")
            .attr("class", "record");

        recordEnter.append("div")
            .attr("class", "time")
            .classed("ram", function (d) { return d.instance; })
            .text(function (d) { return d.instance; });

        recordEnter.append("div")
            .attr("class", "ram")
            .classed("ram", function (d) { return d.ram; })
            .text(function (d) { return parseInt(d.ram, 10); });


        recordEnter.append("div")
            .attr("class", "cpu")
            .classed("cpu", function (d) { return d.cpu; })
            .text(function (d) { return parseInt(d.cpu, 10); });

        recordEnter.append("div")
            .attr("class", "la1")
            .classed("la1", function (d) { return d.La1; })
            .text(function (d) { return parseInt(d.La1, 10); });


        record.exit().remove();

        record.order();
    });
}

// Renders the specified chart or list.
function render(method) {
    d3.select(this).call(method);
}


    // Whenever the brush moves, re-rendering everything.
function renderAll() {
    chart.each(render);
    list.each(render);
    d3.select("#active").text(formatNumber(all.value()));
}

function barChart() {
    if (!barChart.id) {barChart.id = 0; };
    var margin = {top: 10, right: 10, bottom: 20, left: 10},
        x,
        y = d3.scale.linear().range([100, 0]),
        id = barChart.id++,
        axis = d3.svg.axis().orient("bottom"),
        brush = d3.svg.brush(),
        brushDirty,
        dimension,
        group,
        round;

    function chart(div) {

        var width = x.range()[1],
            height = y.range()[0];
        y.domain([0, group.top(1)[0].value]);

        function resizePath(d) {
            var e = +(d === "e"),
                x = e ? 1 : -1,
                y = height / 3;
            return "M" + (0.5 * x) + "," + y
                + "A6,6 0 0 " + e + " " + (6.5 * x) + "," + (y + 6)
                + "V" + (2 * y - 6)
                + "A6,6 0 0 " + e + " " + (0.5 * x) + "," + (2 * y)
                + "Z"
                + "M" + (2.5 * x) + "," + (y + 8)
                + "V" + (2 * y - 8)
                + "M" + (4.5 * x) + "," + (y + 8)
                + "V" + (2 * y - 8);
        }


        function barPath(groups) {
            var path = [],
                i = -1,
                n = groups.length,
                d;
            while (++i < n) {
                d = groups[i];
                path.push("M", x(d.key), ",", height, "V", y(d.value), "h9V", height);
            }
            return path.join("");
        }

        div.each(function () {
            var div = d3.select(this),
                g = div.select("g");

            // Create the skeletal chart.
            if (g.empty()) {
                div.select(".title").append("a")
                    .attr("href", "javascript:reset(" + id + ")")
                    .attr("class", "reset")
                    .text("reset")
                    .style("display", "none");

                g = div.append("svg")
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                g.append("clipPath")
                        .attr("id", "clip-" + id)
                        .append("rect")
                        .attr("width", width)
                        .attr("height", height);

                g.selectAll(".bar")
                        .data(["background", "foreground"])
                        .enter().append("path")
                        .attr("class", function (d) { return d + " bar"; })
                        .datum(group.all());

                g.selectAll(".foreground.bar")
                        .attr("clip-path", "url(#clip-" + id + ")");

                g.append("g")
                        .attr("class", "axis")
                        .attr("transform", "translate(0," + height + ")")
                        .call(axis);

                    // Initialize the brush component with pretty resize handles.
                gBrush = g.append("g").attr("class", "brush").call(brush);
                gBrush.selectAll("rect").attr("height", height);
                gBrush.selectAll(".resize").append("path").attr("d", resizePath);
            }

                // Only redraw the brush if set externally.
            if (brushDirty) {
                brushDirty = false;
                g.selectAll(".brush").call(brush);
                div.select(".title a").style("display", brush.empty() ? "none" : null);
                if (brush.empty()) {
                    g.selectAll("#clip-" + id + " rect")
                        .attr("x", 0)
                        .attr("width", width);
                } else {
                    extent = brush.extent();
                    g.selectAll("#clip-" + id + " rect")
                        .attr("x", x(extent[0]))
                        .attr("width", x(extent[1]) - x(extent[0]));
                }
            }

            g.selectAll(".bar").attr("d", barPath);
        });
    }

    brush.on("brushstart.chart", function () {
        var div = d3.select(this.parentNode.parentNode.parentNode);
        div.select(".title a").style("display", null);
    });

    brush.on("brush.chart", function () {
        var g = d3.select(this.parentNode),
            extent = brush.extent();
        if (round) {g.select(".brush")
                .call(brush.extent(extent = extent.map(round)))
                .selectAll(".resize")
                    .style("display", null)
                   };
        g.select("#clip-" + id + " rect")
            .attr("x", x(extent[0]))
            .attr("width", x(extent[1]) - x(extent[0]));
        dimension.filterRange(extent);
    });

    brush.on("brushend.chart", function() {
        if (brush.empty()) {
            var div = d3.select(this.parentNode.parentNode.parentNode);
            div.select(".title a").style("display", "none");
            div.select("#clip-" + id + " rect").attr("x", null).attr("width", "100%");
            dimension.filterAll();
        }
    });

        chart.margin = function(_) {
            if (!arguments.length) return margin;
            margin = _;
            return chart;
        };

        chart.x = function(_) {
            if (!arguments.length) return x;
            x = _;
            axis.scale(x);
            brush.x(x);
            return chart;
        };

        chart.y = function(_) {
            if (!arguments.length) return y;
            y = _;
            return chart;
        };

        chart.dimension = function(_) {
            if (!arguments.length) return dimension;
            dimension = _;
            return chart;
        };

        chart.filter = function(_) {
            if (_) {
                brush.extent(_);
                dimension.filterRange(_);
            } else {
                brush.clear();
                dimension.filterAll();
            }
            brushDirty = true;
            return chart;
        };

        chart.group = function(_) {
            if (!arguments.length) return group;
            group = _;
            return chart;
        };

        chart.round = function(_) {
            if (!arguments.length) return round;
            round = _;
            return chart;
        };

        return d3.rebind(chart, brush, "on");
    }



function update_graph(records) {
    // A nest operator, for grouping the record list.
    nestByDate = d3.nest()
        .key(function (d) {return d.instance; });

    // A little coercion, since the CSV is untyped.
    records.forEach(function (d, i) {
        d.index = i;
        d.date = parseDate(d.date);
        d.ram = +d.ram;
    });

    // Create the crossfilter for the relevant dimensions and groups.
    record = crossfilter(records);
    all = record.groupAll();
    date = record.dimension(function (d) { return d3.time.day(d.date); });
    dates = date.group();
    hour = record.dimension(function (d) { return d.date.getHours() + d.date.getMinutes() / 60; });
    hours = hour.group(Math.floor);
    ram = record.dimension(function (d) { return d.ram; });
    rams = ram.group(function (d) {return Math.floor(d / 10) * 10; });
    cpu = record.dimension(function (d) {return d.cpu; });
    cpus = cpu.group(function (d) {return Math.floor(d / 10) * 10; });
    la1 = record.dimension(function (d) {return d.La1; });
    la1s = la1.group(function (d) {return Math.floor(d); });
    //      distance = record.dimension(function(d) { return Math.min(1999, d.distance); }),
    //      distances = distance.group(function(d) { return Math.floor(d / 50) * 50; });

    charts = [

        barChart()
            .dimension(hour)
            .group(hours)
            .x(d3.scale.linear()
                 .domain([0, 24])
                 .rangeRound([0, 10 * 24])),

        barChart()
            .dimension(ram)
            .group(rams)
            .x(d3.scale.linear()
                 .domain([0, 100])
                 .rangeRound([0, 10 * 15])),

        barChart()
            .dimension(cpu)
            .group(cpus)
            .x(d3.scale.linear()
                 .domain([0, 100])
                 .rangeRound([0, 10 * 21])),

        barChart()
            .dimension(la1)
            .group(la1s)
            .x(d3.scale.linear()
                 .domain([0, 10])
                 .rangeRound([0, 10 * 21])),

        barChart()
            .dimension(date)
            .group(dates)
            .round(d3.time.day.round)
            .x(d3.time.scale()
                 .domain([new Date(2012, 0, 1), new Date(2012, 1, 1)])
                 .rangeRound([0, 10 * 90]))
        //.filter([new Date(2012, 0, 1), new Date(2012, 1, 1)])
    ];

    // Given our array of charts, which we assume are in the same order as the
    // .chart elements in the DOM, bind the charts to the DOM and render them.
    // We also listen to the chart's brush events to update the display.
    chart = d3.selectAll(".chart")
        .data(charts)
        .each(function (chart) { chart.on("brush", renderAll).on("brushend", renderAll); });

    // Render the initial lists.
    list = d3.selectAll(".list")
        .data([recordList]);

    // Render the total.
    d3.selectAll("#total")
        .text(formatNumber(record.size()));

    renderAll();

    


    window.filter = function (filters) {
        filters.forEach(function (d, i) { charts[i].filter(d); });
        renderAll();
    };

    window.reset = function (i) {
        charts[i].filter(null);
        renderAll();
    };

};

function updateState(){
    $.ajax({
        type:"GET",
        url: url,
        success: function(response){
            update_graph(response)
        }
    })
};

$(document).ready(function(){
if (typeof(remote_url) === 'undefined') {
    url = window.location.pathname
    }else{
        url = remote_url
    }
    console.log(url)
   setInterval( "updateState()", 6000 );
    updateState()
})

