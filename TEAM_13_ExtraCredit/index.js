function map(mapdata, stateColors, caseData) {
  const width = 1000,
        height = 610;

  // Create an SVG element to hold our map
  const svg = d3.select("#map").append("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [0, 0, width, height])
      .attr("style", "width: 100%; height: auto; height: intrinsic;");

  // Add title to the SVG
  svg.append("text")
    .attr("x", width / 2)
    .attr("y", 30)  // Adjust vertical position as needed
    .attr("text-anchor", "middle")
    .attr("font-size", "24px")
    .attr("font-weight", "bold")
    .text("Top 10 Hotspots By State"); // Your desired title

  // Create the US boundary
  const usa = svg.append('g')
      .append('path')
      .datum(topojson.feature(mapdata, mapdata.objects.nation))
      .attr('d', d3.geoPath());

  // Create a color scale for varying shades of the same color
  const colorScale = d3.scaleSequential(d3.interpolateRgb("lightblue", "darkblue")); // Change "lightblue" and "darkblue" to your desired light and dark shades

  // Create the state boundaries
  const states = svg.append('g')
      .attr('stroke', '#444')
      .selectAll('path')
      .data(topojson.feature(mapdata, mapdata.objects.states).features)
      .join('path')
      .attr('vector-effect', 'non-scaling-stroke')
      .attr('d', d3.geoPath())
      .attr('fill', d => stateColors[d.properties.name] ? colorScale(stateColors[d.properties.name]) : 'white'); // Apply custom fill color based on color scale

  // Render dots for case data
  const projection = d3.geoAlbersUsa()
      .scale(1280)
      .translate([width / 2, height / 2]);

  // Define a linear scale for dot sizes based on cases values
  const radiusScale = d3.scaleLinear()
      .domain([0, d3.max(caseData, d => d.cases)]) // Domain: [0, maximum cases value]
      .range([5, 20]); // Range: [minimum dot radius, maximum dot radius]

  // Append circles for dots
  svg.selectAll('.dot')
      .data(caseData)
      .enter().append('circle')
      .attr('class', 'dot')
      .attr('cx', d => projection([d.longitude, d.latitude])[0])
      .attr('cy', d => projection([d.longitude, d.latitude])[1])
      .attr('r', d => radiusScale(d.cases)) // Set dot radius based on cases value
      .attr('fill', 'orange') // Change dot color here
      .attr('opacity', 0.7); // Adjust the opacity of the dot

  // Create legend for state colors and case numbers
  const legend = svg.append('g')
      .attr('class', 'legend')
      .attr('transform', `translate(${width - 150}, ${height - 200})`); // Adjust position of legend

  // Add rectangles for state colors in legend
  legend.selectAll('.legend-color')
      .data(Object.entries(stateColors))
      .enter().append('rect')
      .attr('class', 'legend-color')
      .attr('x', 0)
      .attr('y', (d, i) => i * 20)
      .attr('width', 10)
      .attr('height', 10)
      .attr('fill', ([state, color]) => colorScale(color))
      .attr('stroke', 'black');

  // Add text for state names and case numbers in legend
  legend.selectAll('.legend-text')
      .data(caseData)
      .enter().append('text')
      .attr('class', 'legend-text')
      .attr('x', 30)
      .attr('y', (d, i) => i * 20 + 10)
      .text(d => `${d.state}: ${d.cases}`)
      .attr('fill', 'black')
      .attr('alignment-baseline', 'middle');
}

window.addEventListener('DOMContentLoaded', async (event) => {
  const res = await fetch(`https://cdn.jsdelivr.net/npm/us-atlas@3/states-albers-10m.json`);
  const mapJson = await res.json();

  // Define colors for highlighted states (using a value between 0 and 1 to represent lightness/darkness)
  const stateColors = {
    'Washington': 1.0, // Example value, adjust as needed
    'California': 0.95, // Example value, adjust as needed
    'Ohio': 0.90,
    'Florida': 0.85,
    'Oregon': 0.80,
    'Illinois': 0.75,
    'Texas': 0.70,
    'Michigan': 0.65,
    'Missouri': 0.60,
    'Colorado': 0.55,
    'Georgia': 0.50,
    'Pennsylvania': 0.45,
    'Kentucky': 0.40,
    'New York': 0.35,
    'West Virginia': 0.30,
    'Arkansas': 0.25,
    'Oklahoma': 0.20,
    'Tennessee': 0.10,
    'Idaho': 0.09,
    'Alabama': 0.08,
    'North Carolina': 0.07,
    'Arizona': 0.06,
    'Wisconsin': 0.05,
    'Indiana': 0.04,
    'Virginia': 0.03,
    'Minnesota': 0.02,
    'New Jersey': 0.01,
    'Utah': 0.01,
    'Iowa': 0.01,
    'Montana': 0.01,
    'Kansas': 0.01,
    'Louisiana': 0.01,
    'New Mexico': 0.01,
    'South Carolina': 0.01,
    'Maryland': 0.01,
    'Massachusetts': 0.01,
    'Wyoming': 0.01,
    'Mississippi': 0.01,
    'Alaska': 0.01,
    'Connecticut': 0.01,
    'Maine': 0.01,
    'Nebraska': 0.01,
    'New Hampshire': 0.01,
    'South Dakota': 0.01,
    'Vermont': 0.01
    // Add more states and values as needed
  };

  // Sample data for cases (replace with your actual data)
  const caseData = [
    { state: 'Washington', latitude: 47.400902, longitude: -121.490494, cases: 603 },
    { state: 'California', latitude: 36.116203, longitude: -119.681564, cases: 417 },
    { state: 'Ohio', latitude: 40.388783, longitude: -82.764915, cases: 304 },
    { state: 'Florida', latitude: 27.766279, longitude: -81.686783, cases: 301 },
    { state: 'Oregon', latitude: 44.572021, longitude: -122.070938, cases: 249 },
    { state: 'Illinois', latitude: 40.349457, longitude: -88.986137, cases: 238 },
    { state: 'Texas', latitude: 31.054487, longitude: -97.563461, cases: 233 },
    { state: 'Michigan', latitude: 43.326618, longitude: -84.536095, cases: 216 },
    { state: 'Missouri', latitude: 38.456085, longitude: -92.288368, cases: 159 },
//    { state: 'Colorado', latitude: 39.059811, longitude: 39.059811, cases: 127 }
    // Add more case data as needed
  ];

  map(mapJson, stateColors, caseData);
});
