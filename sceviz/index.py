#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Reads JSON-Schema and converts it to Cytoscape.js format

from flask import (Blueprint, render_template, url_for, current_app)

from pandas import json_normalize

import json, pprint

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    schema = parse_schema(load_schema('uploads/schema.json'))
    return render_template('base.html', schema=schema)


def load_schema(path: str) -> dict:
    """Loads JSON-Schema from file and returns a dict

        Parameters
        ----------
        path : str
            Path to JSON-Schema file

        Returns
        -------
        dict
            A nested dict containing JSON-Schema
        """
    with current_app.open_resource(path) as file:
        schema = json.load(file)
        return schema


def create_node(id: str, label: str = None, node_type: str = None,
                description: str = None, content: str = None) -> dict:
    """Creates a Cytoscape node

        Parameters
        ----------
        id : str
            Unique identifier in the form of an absolute path to that node
        label : str, optional
            A name for displaying

        Returns
        -------
        dict
            A dict containing a Cytoscape node

        Notes
        -----
        Cytoscape format:
            { data: { id: 1, label: 'some label' } }
    """
    return {'data': {'id': id, 'label': label, 'type': node_type,
            'description': description, 'content': content},
            'grabbable': False}


def create_edge(id: str, source: str, target: str) -> dict:
    """Creates a Cytoscape edge

        Parameters
        ----------
        id : str
            Unique ID consisting of the parents ID and the last part of the
            child's ID
        source : str
            ID of the edge starting-node
        target : str
            ID of the edges ending-node

        Returns
        -------
        dict
            A dict containing a Cytoscape edge

        Notes
        -----
        Edge: A---->B:
            { data: { id: 'A->B', source: 'A', target: 'B'  } }
    """

    return {'data': {'id': id, 'source': source, 'target': target}}


def parse_schema(schema: dict,
                 parent: str = "#",
                 data: list = [],
                 index: str = "") -> list:
    """Takes JSON-Schema and converts it to cytoscape format

        Parameters
        ----------
        schema : dict
            Dictionary containing a JSON-Schema
        parent : str
            The parent node of the current layer. used for creating unique ids
        data : list, optional
            List for storing the Cytoscape data. Is returned at the end
        index : str, optional
            Used for ensuring uniqueness in arrays

        Returns
        -------
        list of dict
            A list dictionaries conforming to the Cytoscape format.
    """
    if not data:
        # Data is empty i.e. current node is root
        data.append(create_node('#',schema.get('title', 'root'),
                                    schema.get('type', None),
                                    schema.get('description', None)))

    for key, value in schema.items():
        # Referencing requires unique id for nodes, we use the path from root
        id = parent + '/' + key + index
        edge_id = parent + '->' + key + index

        if isinstance(value, dict):
            # If the child node is a dict we can call parse_schema() recursivly

            # Check for annotations
            node_type = value.get('type', 'JSON Schema')
            description = value.get('description', None)
            node_label = value.get('title', key)

            if not isinstance(node_label, str):
                node_label = key
            
            data.append(create_node(id, node_label, node_type, description))
            data.append(create_edge(edge_id, parent, id))
            parse_schema(value, id, data)
        elif isinstance(value, list):
            # If the child node is a list we have to handle that differently
            # depending on the list's items' type
            content = None

            if key == 'type':
                continue

            if any( isinstance(elem,str) for elem in value ):
                content = value

            data.append(create_node(id, key, 'array', content=content))
            data.append(create_edge(edge_id, parent, id))
            # Arrays can lead to redundant ids and thus we number them to
            # ensure uniqueness.
            for elem in enumerate(value):
                if isinstance(elem[1], dict):
                    parse_schema(elem[1], id, data, str(elem[0]))
        elif key in ['title','type','description']:
            continue
        elif key == '$ref':
            continue
        else:
            data.append(create_node(id, key, content=value))
            data.append(create_edge(edge_id, parent, id))

    return data

def new_parse_schema(schema: dict):
    schema = json_normalize(schema, sep='/',record_prefix='oneOf').to_dict('records')[0]
    # TODO use flatten_json for this!
    flat_schema = {}

    for key, value in schema.items():
        path = key.split('/')
        path_len = len(path)

        for i in range(path_len):
            node_id = '/'.join(path[:i+1])

            if i == path_len - 1:
                flat_schema[node_id] = value
            else:
                flat_schema[node_id] = node_id

    return flat_schema

def resolve_lists(schema: dict):

    for key, value in schema.items():
        if isinstance(value, list):
            for elem in value:
                if isinstance(elem, dict):
                    pass


if __name__ == "__main__":
    file = json.load(open('uploads/schema.json'))
    pprint.pprint(new_parse_schema(file))




        

