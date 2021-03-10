#Reads JSON-Schema and converts it to Cytoscape.js format

import json
from pprint import pprint

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
    with open(path) as file:
        schema = json.load(file)
        return schema

def create_node(id: str, label: str = None, type: str = None) -> dict:
    """Creates a Cytoscape node
        
        Parameters
        ----------
        id : str
            Unique identifier in the form of an absolute path to that node
        label : str, optional
            A name for displaying
        type : str, optional
            Type of the element (string,boolean,...)
            
        Returns
        -------
        dict
            A dict containing a Cytoscape node

        Notes
        -----
        Cytoscape format:
            { data: { id: 1, ... } }
    """
    return { 'data': { 'id': id, 'label': label, 'type': type } }

def create_edge(id: str, source: str, target: str) -> dict:
    """Creates a Cytoscape edge
        
        Parameters
        ----------
        id : str
            Unique identifier. This is required by Cytoscape for further
            referenceing, however, since that isn't required here we
            supply a meaningless autoincremeted number.
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
            { data: { id: 'AB', source: 'A', target: 'B'  } }
    """

    return { 'data': { 'id': id, 'source': source, 'target': target } } 

    

def parse_schema(schema: dict, parent: str = "#", data: list = []) -> list:
    """Takes JSON-Schema and converts it to cytoscape format
        
        Parameters
        ----------
        schema : dict
            Dictionary containing a JSON-Schema
        parent : str
            The parent node of the current layer. used for creating unique ids
        data : list, optional
            List for storing the Cytoscape data. Is returned at the end

        Returns
        -------
        list of dict
            A list dictionaries conforming to the Cytoscape format.
    """
    for key, value in schema.items():
        #For paths we need to identify the parent node thus every
        #node receives its path as an id
        id = parent + '/' + key
        edge_id = parent.split('/')[-1] + '-' + key
        if isinstance(value,dict):
            #Value is complex i.e. needs further traversal
            #Check whether value is a JSON-object
            if 'properties' in value:
                data.append(create_node(id,key,value['type']))
                data.append(create_edge(edge_id,parent,id))
                parse_schema(value['properties'],id,data)
            else:
                #Value isn't an object i.e. we've reached a leaf
                data.append(create_node(id,key,value['type']))
                data.append(create_edge(edge_id,parent,id))

        else:
            

    return data

if __name__ == '__main__':
    pprint(parse_schema(load_schema('schema.json')))