var cy = cytoscape({
    container: document.getElementById('cy'),
    elements: schema,
    // styling and layout
    layout: {
        name: 'circle'
    },
    style: [
        {
            selector: 'node',
            style: {
                shape: 'square',
                'background-color': 'green',
                label: 'data(id)'
            }
        }
    ]
});