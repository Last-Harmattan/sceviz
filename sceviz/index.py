#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Reads JSON-Schema and converts it to Cytoscape.js format

from logging import INFO
import os

import secrets

from flask import (Blueprint, render_template, url_for, redirect,
                    flash, request, current_app, abort, session)

from pandas import json_normalize

from werkzeug.utils import secure_filename

from flatten_json import flatten, flatten_preserve_lists

from json import load

from pprint import pprint


bp = Blueprint('index', __name__)

colors = {"delete":"#d1364e",
          "add":"#609462",
          "rename":"#f7c548",
          "copy":"#96c5f7",
          "move":"#2c1452"}

@bp.route('/',methods=['GET'])
def index():

    if 'id' not in session:
        session['id'] = secrets.token_urlsafe(16)

    filename = session['id'] + '.json'

    try:
        schemas = load_schemas(os.path.join(
            'uploads',
            filename
        ))
    except FileNotFoundError:
        schemas = load_schemas(os.path.join(
            'uploads',
            'evolution.json'
        ))

    evolution = load_evolution(os.path.join(
        'uploads',
        'evolution.json'
    ))

    return render_template('base.html', schemas=schemas, evolution=evolution)

@bp.route('/',methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    filename = uploaded_file.filename

    if filename != '':
        file_ext = os.path.splitext(filename)[1]

        if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
            abort(400)

        filename = session['id'] + '.json'
        uploaded_file.save(os.path.join(current_app.config['UPLOAD_PATH'],
                                        filename))
    
    return redirect(url_for('index'))


def load_schemas(path: str)-> list:
    data = {}

    with current_app.open_resource(path) as file:
        schemas = load(file)

    schemas = schemas['schemas']

    for schema in schemas:
        data[schema['$id']] = parse_schema(schema)

    return data


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
        schema = load(file)
        return schema

def load_evolution(path: str) -> dict:

    data = []

    with current_app.open_resource(path) as file:
        evolution = load(file)

    for index, schema in enumerate(evolution['schemas']):
        node = {"data": {
            "id": schema['$id'],
            "label": f'v{index}'
        }}

        data.append(node)

    for operation in evolution['operations']:
        edge = {"data": {
            'operation': parse_operation(operation['operation']),
            'op': colors[operation['operation'].split(' ')[0]],
            'source': operation['source'],
            'target': operation['destination'],
            'subject': node_from_operation(operation['operation'])
        }}

        data.append(edge)

    return data


def node_from_operation(op: str) -> str:
    op = op.split(' ')

    if op[0] in ['add','delete']:
        path = op[1].replace('.','/properties/')
        path = path.split('/')
        path[0] = '#'
        return '/'.join(path)
    elif op[0] == 'rename':
        path = op[1].replace('.','/properties/')
        path = path.split('/')
        path[0] = '#'
        path[-1] = op[3]
        return '/'.join(path)
    else:
        return None


def parse_operation(op: str) -> str:
    op = op.split(' ')

    if op[0] in ['add','delete']:
        return f'{op[0]} {op[1]}'
    else:
        return f'{op[0]} {op[1]} to {op[3]}'

def flatten_schema(schema: dict):
    schema = flatten(schema,separator='/')
    flat_schema = {}

    for key, value in schema.items():
        path = key.split('/')
        path_len = len(path)

        for i in range(path_len):
            node_id = '/'.join(path[:i+1])

            if i == path_len - 1:
                flat_schema[node_id] = value
            elif path[-1] in ['$ref','$schema','$id']:
                flat_schema[node_id] = value 
            else:
                flat_schema[node_id] = node_id

    return flat_schema


def resolve_lists(schema: dict) -> dict:

    for key, value in schema.copy().items():
        path = key.split('/')
        parent_path = '/'.join(path[:-1])
        if path[-1].isdigit():
            if isinstance(schema[parent_path],list):
                schema[parent_path].append(value)
                del schema[key]
            else:
                schema[parent_path] = [value]
                del schema[key]
    
    return schema


def convert_cytoscape(schema: dict):

    # Adding the root node and removing it's annotations
    data = [{
        'data': {
            'id': '#',
            'label': schema.pop('title','root'),
            'type': schema.pop('type','object'),
            'description': schema.pop('description', None)
        }
    }]

    for key, value in schema.items():
        path = key.split('/')
        
        if not path[:-1]:
            parent_path = '#'
        else:
            if path[:-1][-1].isdigit():
                # If node is a list item we have to remove its number id from
                # the parent path
                parent_path = '#/' + '/'.join(path[:-2])
            else:
                parent_path = '#/' + '/'.join(path[:-1])

        if path[-1] == 'type':
            continue

        node = {'group': 'nodes',
        'data': {
            'id': '#/' + key,
            'label': schema.get(key + '/title', path[-1]),
            'type': schema.get(key + '/type', "JSON Schema Keyword"),
            'description': schema.get(key + '/description', None)
        }}

        edge = {'group': 'edges',
        'data': {
            'source': parent_path,
            'target': '#/' + key
        }}

        if isinstance(value, list):
            node['data']['content'] = value
        elif key != value:
            node['data']['content'] = value
        else:
            node['data']['content'] = None

        data.append(node)
        data.append(edge)
    
    return data

def resolve_reference(schema: dict):
    
    for key, value in schema.copy().items():
        path = key.split('/')
        parent_path = '/'.join(path[:-1])

        # If the node is not  a '$ref' than it shouldn't have a path as value
        if value[0] == '#':
            schema[key] = None

        if path[-1] == '$ref':
            del schema[key]
            schema[parent_path] = value

    return schema


def parse_schema(schema):
    schema = flatten_schema(schema)
    schema = resolve_lists(schema)
    schema = resolve_reference(schema)
    return convert_cytoscape(schema)



if __name__ == "__main__":
    #pprint(load_schemas('uploads/evolution.json'))
    print('Simba!')