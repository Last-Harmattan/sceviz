import os

from flask import (
    Flask, render_template, flash, request, redirect, url_for
)

def create_app(test_config=None):
    """Application Factory"""
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'sceviz.sqlite'),
        UPLOAD_FOLDER = '/uploads'
    )

    if test_config is None:
        app.config.from_pyfile('config.py',silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import index
    app.register_blueprint(index.bp)
    app.add_url_rule('/',endpoint='index')

    return app