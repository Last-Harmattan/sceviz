#Reads JSON-Schema and converts it to Cytoscape.js format

import json

def load_schema(file):
    with open(file) as schema:
        