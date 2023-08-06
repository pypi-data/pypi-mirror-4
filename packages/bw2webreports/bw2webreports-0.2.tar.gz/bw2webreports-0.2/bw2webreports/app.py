# -*- coding: utf-8 -*-
from __future__ import division
from flask import Flask, render_template, request, abort
import json
import os

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return "Resource not found", 404


@app.errorhandler(500)
def internal_error(e):
    return "Application error", 500


@app.route("/upload", methods=["POST"])
def upload():
    data = request.json
    if not data or not isinstance(data, dict) or "metadata" not in data \
            or not data["metadata"].get("uuid", None) \
            or not data["metadata"].get("type", None) == \
            u"Brightway2 serialized LCA report":
        abort(400)
    filepath = os.path.join(app.config["DATA_DIR"],
        "%s.json" % data["metadata"]["uuid"])
    with open(filepath, "w") as f:
        json.dump(data, f)
    return "OK"


@app.route('/report/<uuid>')
def report(uuid):
    try:
        data = open(os.path.join(app.config["DATA_DIR"], "%s.json" % uuid)).read()
    except:
        return render_template('404.html'), 404
    return render_template("report.html", data=data)


@app.route('/status')
def status():
    return json.dumps({'reports': len(os.listdir(app.config["DATA_DIR"]))})

# TODO: Prevent large uploads
# TODO: Prevent overwriting of existing reports
