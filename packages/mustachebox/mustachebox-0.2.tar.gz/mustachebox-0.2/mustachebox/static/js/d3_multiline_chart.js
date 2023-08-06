data = data.map( function (d) {
    return {
      serie: +d.serie,   // the + sign will coerce strings to number values
      date: new Date(d.date),
      value: +d.value };
});


var x = d3.time.scale()
        .range([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

x.domain(d3.extent(data, function(d) {return d.date; }));

data = d3.nest().key(function(d) { return d.serie; }).entries(data);





var line = d3.svg.line()
    .interpolate("basis")
    .x(function(d) {return x(d.date); })
    .y(function(d) {return y(d.value); });

var color = d3.scale.category10();

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

y.domain([
    d3.min(data, function(c) {
        return d3.min(c.values, function(v) { return v.value; }); }),
    d3.max(data, function(c) {
        return d3.max(c.values, function(v) { return v.value; }); })
  ]);




var svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)

var serie = svg.selectAll(".serie")
      .data(data)
    .enter().append("g")
      .attr("class", "serie");

serie.append("path")
      .attr("class", "line")
      .attr("d", function(d){return line(d.values)})
      .style("stroke", function(d) {return color(d.key); });

