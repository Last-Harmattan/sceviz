var cy = cytoscape({
    container: document.getElementById('cy'),
    elements: [
        // nodes
        { data: { id: 'a' } },
        { data: { id: 'b' } },
        { data: { id: 'c' } },
        { data: { id: 'd' } },
        { data: { id: 'e' } },
        { data: { id: 'f' } },
        
        // edges
        {
            data: {
                id: 'ab',
                source: 'a',
                target: 'b'
            }
        },
        {
            data: {
                id: 'cd',
                source: 'c',
                target: 'd'
        }
        },
        {
            data: {
                id: 'ef',
                source: 'e',
                target: 'f'
            }
        },
        {
            data: {
                id: 'ac',
                source: 'a',
                target: 'c'
        }
        },
        {
            data: {
                id: 'be',
                source: 'b',
                target: 'e'
            }
        }
    ],
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