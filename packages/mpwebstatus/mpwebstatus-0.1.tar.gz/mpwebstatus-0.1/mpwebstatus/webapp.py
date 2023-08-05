# -*- coding: utf-8 -*-
from flask import Flask, request, render_template
import json
import time

app = Flask(__name__)

global datastore
datastore = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/update/<task>", methods=["POST"])
def update(task):
    data = json.loads(request.data)
    if task not in datastore:
        data["_born"] = data["_ping"] = time.time()
    else:
        data["_ping"] = time.time()
        data["_born"] = datastore[task]["_born"]
    datastore[task] = data
    return ""


@app.route("/status")
def status():
    print datastore
    d = [{
        "task": k,
        "eta": v.get("eta", 0),
        "elapsed": time.time() - v.get("_born", 0),
        "ping": v.get("_ping", 0),
        "finished": v.get("finished", False),
        "progress": v.get("progress", 0),
        "total": v.get("total", 0),
        } for k, v in datastore.iteritems()]
    d.sort(key=lambda x: x["task"])
    return json.dumps(d)
