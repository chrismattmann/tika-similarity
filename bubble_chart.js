var diameter = 900, //max size of the bubbles
  color = d3.scale.category20(); //color category

var bubble = d3.layout
  .pack()
  .sort(null)
  .size([diameter, diameter])
  .padding(1.5);

var svg = d3
  .select("body")
  .append("svg")
  .attr("width", diameter)
  .attr("height", diameter)
  .attr("class", "bubble");

d3.csv("/bubble_chart_data.csv", function (data) {
  var x2values = {};
  for (var i = 0; i < data.length; i++) {
    if (data[i]["x-coordinate"]) {
      if (data[i]["Similarity_score"]) {
        x2values[data[i]["x-coordinate"]] = data[i]["Similarity_score"];
      }
    }
  }
  console.log(x2values);

  // Create array of objects of search results to be used by D3
  var d = [];
  for (var key in x2values) {
    var val = x2values[key];
    d.push({
      count: val,
      keyword: key,
    });
  }
  console.log("data is: ", d);

  //convert numerical values from strings to numbers
  d = d.map(function (data) {
    data.value = +data["count"];
    return data;
  });

  //bubbles needs very specific format, convert data to this.
  var nodes = bubble.nodes({ children: d }).filter(function (data) {
    return !data.children;
  });

  //setup the chart
  var bubbles = svg
    .append("g")
    .attr("transform", "translate(0,0)")
    .selectAll(".bubble")
    .data(nodes)
    .enter();

  //create the bubbles
  bubbles
    .append("circle")
    .attr("r", function (d) {
      return d.r;
    })
    .attr("cx", function (d) {
      return d.x;
    })
    .attr("cy", function (d) {
      return d.y;
    })
    .transition()
    .ease("elastic")
    .duration(3000)
    .style("fill", function (d) {
      return color(d.value);
    });

  //format the text for each bubble
  bubbles
    .append("text")
    .attr("x", function (d) {
      return d.x;
    })
    .attr("y", function (d) {
      return d.y + 5;
    })
    .attr("text-anchor", "middle")
    .text(function (d) {
      return d["keyword"];
    })
    .style({
      fill: "black",
      "font-family": "Helvetica Neue, Helvetica, Arial, san-serif",
      "font-size": "12px",
    });
});
