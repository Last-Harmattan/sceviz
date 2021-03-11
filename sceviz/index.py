#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Reads JSON-Schema and converts it to Cytoscape.js format

from flask import (
    Blueprint, render_template, url_for, current_app
)

import json

bp = Blueprint('index',__name__)

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

def create_node(id: str, label: str = None) -> dict:
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
    return { 'data': { 'id': id, 'label': label }, 'grabbable': False }

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

    return { 'data': { 'id': id, 'source': source, 'target': target } } 

    

def parse_schema(schema: dict, parent: str = "#",
                data: list = [], index: str = "") -> list:
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
        #Data is empty i.e. current node is root
        try:
            #Use specific title if given
            data.append(create_node('#',schema['title']))
        except KeyError:
            #and generic if not
            data.append(create_node('#','root'))

    for key, value in schema.items():
        #Referencing requires unique id for nodes, we use the path from root
        id = parent + '/' + key + index
        edge_id = parent + '->' + key + index
        
        if isinstance(value, dict):
            #If the child node is a dict we can call parse_schema() recursivly
            data.append(create_node(id,key))
            data.append(create_edge(edge_id,parent,id))
            parse_schema(value,id,data)
        elif isinstance(value, list):
            #If the child node is a list we have to handle that differently
            #depending on the list's items' type
            data.append(create_node(id,key))
            data.append(create_edge(edge_id,parent,id))
            #Arrays can lead to redundant ids and thus we number them to ensure
            #uniqueness.
            for elem in enumerate(value):
                if isinstance(elem[1], dict):
                    parse_schema(elem[1],id,data,str(elem[0]))
        else:
            data.append(create_node(id,key))
            data.append(create_edge(edge_id,parent,id))

    return data