<script>
var graph = new Rickshaw.Graph( {
	element: document.getElementById("{{element_id}}"),
	width: {{width}},
	height: {{height}},
	renderer: 'bar',
	series: [
		{
			color: "#c05020",
			data: {{data}} 
        }
	]
} );

graph.render();
</script>
