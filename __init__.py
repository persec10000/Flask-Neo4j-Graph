from flask import Flask, render_template, Blueprint, flash

import json
import os

app = Flask(__name__, static_folder="templates")
import graph
app.register_blueprint(graph.bp)
app.secret_key = b'rfwefewedfsd'


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
